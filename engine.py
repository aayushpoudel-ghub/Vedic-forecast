"""Vedic 5-Year Forecast Engine — real sidereal computation with antardasha timeline + transits."""
import swisseph as swe
from datetime import datetime, timedelta
import json

SIGNS = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']
NAKS = ['Ashwini','Bharani','Krittika','Rohini','Mrigashira','Ardra','Punarvasu','Pushya','Ashlesha','Magha','P.Phalguni','U.Phalguni','Hasta','Chitra','Swati','Vishakha','Anuradha','Jyeshtha','Mula','P.Ashadha','U.Ashadha','Shravana','Dhanishta','Shatabhisha','P.Bhadrapada','U.Bhadrapada','Revati']
NAK_LORDS = ['Ketu','Venus','Sun','Moon','Mars','Rahu','Jupiter','Saturn','Mercury']*3
DASHA_ORDER = ['Ketu','Venus','Sun','Moon','Mars','Rahu','Jupiter','Saturn','Mercury']
DASHA_YEARS = {'Ketu':7,'Venus':20,'Sun':6,'Moon':10,'Mars':7,'Rahu':18,'Jupiter':16,'Saturn':19,'Mercury':17}
PLANETS = {'Sun':swe.SUN,'Moon':swe.MOON,'Mars':swe.MARS,'Mercury':swe.MERCURY,'Jupiter':swe.JUPITER,'Venus':swe.VENUS,'Saturn':swe.SATURN}
EXALT = {'Sun':0,'Moon':1,'Mars':9,'Mercury':5,'Jupiter':3,'Venus':11,'Saturn':6}
OWN = {'Sun':[4],'Moon':[3],'Mars':[0,7],'Mercury':[2,5],'Jupiter':[8,11],'Venus':[1,6],'Saturn':[9,10]}
DEBIL = {'Sun':6,'Moon':7,'Mars':3,'Mercury':11,'Jupiter':9,'Venus':5,'Saturn':0}
Y = 365.25

def _setup():
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    return swe.FLG_SWIEPH | swe.FLG_SIDEREAL

def compute_chart(year, month, day, hour, minute, lat, lon, tz_offset_hours):
    local = datetime(year, month, day, hour, minute)
    ut = local - timedelta(hours=tz_offset_hours)
    jd = swe.julday(ut.year, ut.month, ut.day, ut.hour + ut.minute/60.0)
    FLG = _setup()

    pos = {}
    for name, pid in PLANETS.items():
        r = swe.calc_ut(jd, pid, FLG)[0]
        pos[name] = {'lon': r[0], 'speed': r[3]}
    rahu = swe.calc_ut(jd, swe.MEAN_NODE, FLG)[0][0]
    pos['Rahu'] = {'lon': rahu, 'speed': -1}
    pos['Ketu'] = {'lon': (rahu+180)%360, 'speed': -1}

    cusps, ascmc = swe.houses_ex(jd, lat, lon, b'P', FLG)
    asc = ascmc[0]; asc_sign = int(asc//30)

    def dignity(name, lon):
        s = int(lon//30)
        if name in EXALT and s == EXALT[name]: return 'Exalted'
        if name in OWN and s in OWN[name]: return 'Own sign'
        if name in DEBIL and s == DEBIL[name]: return 'Debilitated'
        return ''

    chart = {'ascendant': {}, 'planets': {}}
    n = int(asc//(360/27))
    chart['ascendant'] = {'sign': SIGNS[asc_sign], 'sign_idx': asc_sign, 'deg': round(asc%30,2), 'nakshatra': NAKS[n], 'lon': asc}
    for name, d in pos.items():
        l = d['lon']; s = int(l//30)
        house = ((s - asc_sign) % 12) + 1
        nk = int(l//(360/27))
        chart['planets'][name] = {
            'sign': SIGNS[s], 'sign_idx': s, 'deg': round(l%30,2), 'house': house,
            'nakshatra': NAKS[nk], 'nak_lord': NAK_LORDS[nk],
            'retrograde': (d['speed'] < 0 and name not in ['Rahu','Ketu']),
            'dignity': dignity(name, l), 'lon': l
        }

    # Vimshottari dasha with full antardasha timeline
    moon = pos['Moon']['lon']
    nl = 360/27; ni = int(moon//nl); frac = (moon%nl)/nl
    start_lord = NAK_LORDS[ni]; si = DASHA_ORDER.index(start_lord)
    balance = DASHA_YEARS[start_lord]*(1-frac)
    cur = local
    end = cur + timedelta(days=balance*Y)
    mds = [{'lord': start_lord, 'start': cur, 'end': end}]
    cur = end
    for k in range(1, 12):
        ld = DASHA_ORDER[(si+k)%9]
        end = cur + timedelta(days=DASHA_YEARS[ld]*Y)
        mds.append({'lord': ld, 'start': cur, 'end': end})
        cur = end

    now = datetime.now()
    cur_md = next((m for m in mds if m['start'] <= now < m['end']), mds[0])

    def antardashas(md):
        out = []; tot = DASHA_YEARS[md['lord']]; sub = md['start']
        for k in range(9):
            sl = DASHA_ORDER[(DASHA_ORDER.index(md['lord'])+k)%9]
            dur = DASHA_YEARS[sl]*tot/120.0
            se = sub + timedelta(days=dur*Y)
            out.append({'lord': sl, 'start': sub, 'end': se})
            sub = se
        return out

    cur_ads = antardashas(cur_md)
    cur_ad = next((a for a in cur_ads if a['start'] <= now < a['end']), cur_ads[0])

    # Build a 5-year antardasha timeline (may span 2 mahadashas)
    window_end = now + timedelta(days=5*Y)
    timeline = []
    for m in mds:
        if m['end'] < now or m['start'] > window_end: continue
        for a in antardashas(m):
            if a['end'] < now or a['start'] > window_end: continue
            timeline.append({'md': m['lord'], 'ad': a['lord'],
                             'start': a['start'], 'end': a['end']})

    chart['dashas'] = [{'lord': m['lord'], 'start': m['start'].strftime('%Y-%m-%d'), 'end': m['end'].strftime('%Y-%m-%d')} for m in mds[:7]]
    chart['current_mahadasha'] = cur_md['lord']
    chart['current_antardasha'] = cur_ad['lord']
    chart['md_start'] = cur_md['start'].strftime('%Y-%m-%d')
    chart['md_end'] = cur_md['end'].strftime('%Y-%m-%d')
    chart['mahadashas_full'] = [{'lord': m['lord'], 'start': m['start'].strftime('%Y-%m-%d'), 'end': m['end'].strftime('%Y-%m-%d')} for m in mds]
    chart['timeline'] = [{'md': t['md'], 'ad': t['ad'], 'start': t['start'].strftime('%Y-%m-%d'), 'end': t['end'].strftime('%Y-%m-%d')} for t in timeline]

    degs = {nm: chart['planets'][nm]['deg'] for nm in PLANETS}
    chart['darakaraka'] = min(degs, key=degs.get)

    # Saturn & Jupiter transit sign now + their house from this lagna (for sade sati etc.)
    moon_sign = chart['planets']['Moon']['sign_idx']
    sat_now = swe.calc_ut(swe.julday(now.year, now.month, now.day, 12), swe.SATURN, FLG)[0][0]
    jup_now = swe.calc_ut(swe.julday(now.year, now.month, now.day, 12), swe.JUPITER, FLG)[0][0]
    sat_sign = int(sat_now//30); jup_sign = int(jup_now//30)
    chart['saturn_transit_sign'] = SIGNS[sat_sign]
    chart['saturn_house'] = ((sat_sign - asc_sign) % 12) + 1
    chart['jupiter_transit_sign'] = SIGNS[jup_sign]
    chart['jupiter_house'] = ((jup_sign - asc_sign) % 12) + 1
    # sade sati: Saturn in 12th, 1st, or 2nd from Moon sign
    rel = (sat_sign - moon_sign) % 12
    chart['sade_sati'] = rel in (11, 0, 1)
    chart['sade_sati_phase'] = {11:'rising (first phase)', 0:'peak (over your Moon)', 1:'setting (final phase)'}.get(rel, None)

    # ----- Moon phase / Paksha (waxing vs waning) -----
    sun_lon_natal = pos['Sun']['lon']
    moon_lon_natal = pos['Moon']['lon']
    elong = (moon_lon_natal - sun_lon_natal) % 360   # 0=new, 180=full
    chart['moon_elongation'] = round(elong,2)
    # Shukla (waxing) = 0..180 increasing toward full; Krishna (waning) = 180..360
    chart['moon_waxing'] = elong <= 180
    # Paksha Bala proxy 0..1: brightness (1 at full, 0 at new)
    chart['moon_brightness'] = round((1 - abs(180-elong)/180), 3)
    # tithi (lunar day 1-30)
    chart['tithi'] = int(elong // 12) + 1

    # ----- Graha Yuddha (planetary war): two of Mer/Ven/Mar/Jup/Sat within 1 deg -----
    war_planets=['Mercury','Venus','Mars','Jupiter','Saturn']
    wars=[]
    for i in range(len(war_planets)):
        for j in range(i+1, len(war_planets)):
            a,b=war_planets[i],war_planets[j]
            la=pos[a]['lon']; lb=pos[b]['lon']
            sep=abs((la-lb+180)%360-180)
            if sep < 1.0:
                # lower longitude (degree) conventionally wins
                winner = a if (la%30) < (lb%30) else b
                loser = b if winner==a else a
                wars.append({'winner':winner,'loser':loser,'sep':round(sep,3)})
    chart['planetary_wars']=wars

    # ----- Papa/Shubha Kartari around the Moon and the Lagna (hemming) -----
    def hemming(target_house):
        prev_h = ((target_house-2)%12)+1
        next_h = (target_house%12)+1
        prev_occ=[nm for nm,p in chart['planets'].items() if p['house']==prev_h and nm not in ('Rahu','Ketu')]
        next_occ=[nm for nm,p in chart['planets'].items() if p['house']==next_h and nm not in ('Rahu','Ketu')]
        # include nodes for malefic hemming
        prev_all=[nm for nm,p in chart['planets'].items() if p['house']==prev_h]
        next_all=[nm for nm,p in chart['planets'].items() if p['house']==next_h]
        benefics={'Jupiter','Venus','Mercury','Moon'}
        malefics={'Sun','Mars','Saturn','Rahu','Ketu'}
        prev_b=any(x in benefics for x in prev_all); next_b=any(x in benefics for x in next_all)
        prev_m=all(x in malefics for x in prev_all) and len(prev_all)>0
        next_m=all(x in malefics for x in next_all) and len(next_all)>0
        if prev_b and next_b: return 'shubha'   # benefics on both sides
        if prev_m and next_m: return 'papa'      # malefics on both sides
        return None
    moon_h=chart['planets']['Moon']['house']
    chart['moon_kartari']=hemming(moon_h)
    chart['lagna_kartari']=hemming(1)

    return chart

def compute_from_place(year, month, day, hour, minute, lat, lon):
    import places
    tz_offset, tzname = places.offset_for(lat, lon, year, month, day, hour, minute)
    chart = compute_chart(year, month, day, hour, minute, lat, lon, tz_offset)
    chart['timezone'] = tzname
    chart['tz_offset'] = tz_offset
    chart['birth_year']=year; chart['birth_month']=month; chart['birth_day']=day
    return chart

if __name__ == '__main__':
    c = compute_chart(1995, 12, 6, 22, 0, 26.6483, 85.80, 5.75)
    print("Ascendant:", c['ascendant']['sign'], c['ascendant']['deg'])
    print("MD:", c['current_mahadasha'], "AD:", c['current_antardasha'])
    print("Sade sati:", c['sade_sati'], c['sade_sati_phase'])
    print("Saturn house:", c['saturn_house'], "Jupiter house:", c['jupiter_house'])
    print("\n5-year timeline:")
    for t in c['timeline']:
        print(f"  {t['md']}-{t['ad']}: {t['start']} -> {t['end']}")
