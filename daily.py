"""Daily & monthly personalized readings from real transits relative to the natal chart.
Uses the Moon-transit (Gochara) + Tara Bala systems — genuine Vedic daily logic,
not sun-sign generalities. Star rating is computed, not random."""
import swisseph as swe
from datetime import datetime, timedelta

SIGNS=['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']
NAKS=['Ashwini','Bharani','Krittika','Rohini','Mrigashira','Ardra','Punarvasu','Pushya','Ashlesha','Magha','P.Phalguni','U.Phalguni','Hasta','Chitra','Swati','Vishakha','Anuradha','Jyeshtha','Mula','P.Ashadha','U.Ashadha','Shravana','Dhanishta','Shatabhisha','P.Bhadrapada','U.Bhadrapada','Revati']

def _setup():
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    return swe.FLG_SWIEPH | swe.FLG_SIDEREAL

# Moon-sign transit (Chandra Gochara): house of a transiting planet counted from natal Moon sign.
# Classical benefic/malefic transit positions from the Moon:
GOCHARA_GOOD={  # houses (from Moon) where each planet gives good results
 'Sun':[3,6,10,11],'Moon':[1,3,6,7,10,11],'Mars':[3,6,11],'Mercury':[2,4,6,8,10,11],
 'Jupiter':[2,5,7,9,11],'Venus':[1,2,3,4,5,8,9,11,12],'Saturn':[3,6,11],
 'Rahu':[3,6,11],'Ketu':[3,6,11]}

# Tara Bala: the 9-fold star cycle from natal Moon nakshatra to the day's Moon nakshatra.
# Taras 1..9 repeating; some are auspicious, some not.
TARA_QUALITY=[  # index 0..8 -> (name, score -1/0/+1)
 ('Janma',0),('Sampat',1),('Vipat',-1),('Kshema',1),('Pratyak',-1),
 ('Sadhana',1),('Naidhana',-1),('Mitra',1),('Param Mitra',1)]

def positions(jd, FLG):
    out={}
    for nm,pid in [('Sun',swe.SUN),('Moon',swe.MOON),('Mars',swe.MARS),('Mercury',swe.MERCURY),
                   ('Jupiter',swe.JUPITER),('Venus',swe.VENUS),('Saturn',swe.SATURN)]:
        out[nm]=swe.calc_ut(jd,pid,FLG)[0][0]
    r=swe.calc_ut(jd,swe.MEAN_NODE,FLG)[0][0]
    out['Rahu']=r; out['Ketu']=(r+180)%360
    return out

def daily_reading(natal_moon_lon, natal_asc_lon, md_lord, target_date=None):
    """Return star rating (1-5) + structured factors for a given day."""
    FLG=_setup()
    d = target_date or datetime.now()
    jd = swe.julday(d.year, d.month, d.day, 6.0)  # morning
    pos = positions(jd, FLG)

    natal_moon_sign = int(natal_moon_lon//30)
    natal_moon_nak = int(natal_moon_lon//(360/27))
    day_moon_sign = int(pos['Moon']//30)
    day_moon_nak = int(pos['Moon']//(360/27))

    score = 0.0; factors=[]

    # 1. Tara Bala (day Moon nakshatra from natal Moon nakshatra)
    tara_idx = (day_moon_nak - natal_moon_nak) % 9
    tname, tq = TARA_QUALITY[tara_idx]
    score += tq*1.5
    factors.append(('tara', tname, tq))

    # 2. Moon transit house from natal Moon (Chandra Gochara)
    moon_house = ((day_moon_sign - natal_moon_sign) % 12) + 1
    moon_good = moon_house in GOCHARA_GOOD['Moon']
    score += (1.0 if moon_good else -0.7)
    factors.append(('moon_house', moon_house, moon_good))

    # 3. Benefic transits (Jupiter, Venus) position from Moon
    for ben in ['Jupiter','Venus']:
        h = ((int(pos[ben]//30) - natal_moon_sign) % 12) + 1
        good = h in GOCHARA_GOOD[ben]
        score += (0.7 if good else -0.3)
        factors.append((ben, h, good))

    # 4. Malefic transits (Saturn, Mars) position from Moon
    for mal in ['Saturn','Mars']:
        h = ((int(pos[mal]//30) - natal_moon_sign) % 12) + 1
        good = h in GOCHARA_GOOD[mal]
        score += (0.5 if good else -0.6)
        factors.append((mal, h, good))

    # 5. Dasha lord's transit house from Moon (the active planet matters more)
    if md_lord in pos:
        h = ((int(pos[md_lord]//30) - natal_moon_sign) % 12) + 1
        good = h in GOCHARA_GOOD.get(md_lord,[3,6,11])
        score += (0.8 if good else -0.5)
        factors.append(('dasha_lord', md_lord, h, good))

    # Map score (-~5..+~5) to 1..5 stars
    stars = max(1, min(5, round(3 + score*0.55)))

    return {
        'stars': stars,
        'score': round(score,2),
        'tara': tname, 'tara_q': tq,
        'moon_house': moon_house, 'moon_good': moon_good,
        'day_moon_sign': SIGNS[day_moon_sign], 'day_moon_nak': NAKS[day_moon_nak],
        'factors': factors,
        'md_lord': md_lord,
        'date': d.strftime('%Y-%m-%d')
    }

if __name__=='__main__':
    import engine
    c=engine.compute_chart(1995,12,6,22,0,26.6483,85.80,5.75)
    moon_lon=c['planets']['Moon']['lon']; asc_lon=c['ascendant']['lon']
    md=c['current_mahadasha']
    print("Daily readings for the next 7 days (your chart):")
    for i in range(7):
        r=daily_reading(moon_lon, asc_lon, md, datetime.now()+timedelta(days=i))
        print(f"  {r['date']}: {'★'*r['stars']}{'☆'*(5-r['stars'])}  (score {r['score']}, Tara {r['tara']}, Moon in your {r['moon_house']}th from natal)")


# ---------- text layer: short readings keyed to the computed factors ----------

STAR_MOOD={
 5:"An excellent day — the transits strongly favour you.",
 4:"A good, supportive day with the flow mostly with you.",
 3:"A balanced, ordinary day — neither pushed nor blocked.",
 2:"A somewhat challenging day; go gently and don't force things.",
 1:"A demanding day — patience and care will serve you best.",
}

MOON_HOUSE_LINE={
 1:"With the Moon over your own sign, emotions run close to the surface — be mindful of mood.",
 2:"The Moon moves through your money-and-family sphere; matters of home and finances feel closer today.",
 3:"A favourable lunar position for courage and effort — good for initiative and communication.",
 4:"The Moon touches your home and heart; comfort, rest, and family matter more today.",
 5:"A creative, expressive lunar mood — good for learning, romance, and play.",
 6:"The Moon favours work and overcoming obstacles — a productive day for tackling tasks.",
 7:"Focus turns to others and partnership; cooperation goes well, solo pushing less so.",
 8:"An inward lunar position — guard energy, avoid risk, and don't overextend today.",
 9:"A fortunate, expansive lunar mood — good for learning, travel, and the bigger picture.",
 10:"The Moon lifts your visible, working side — a day to be seen and to act publicly.",
 11:"A strong lunar position for gains and friends — networking and goals are favoured.",
 12:"A quiet, restful lunar mood — better for retreat and reflection than big moves.",
}

TARA_LINE={
 'Janma':"a sensitive personal note runs through the day — keep steady",
 'Sampat':"fortune and prosperity are favoured — a lucky thread today",
 'Vipat':"a slightly accident-prone star — take small care with risk",
 'Kshema':"a stable, well-being star — things hold together nicely",
 'Pratyak':"a day of mild obstacles — patience smooths the path",
 'Sadhana':"a productive star for accomplishing what you set out to do",
 'Naidhana':"a low-energy star — rest, and avoid the unnecessary",
 'Mitra':"a friendly, supportive star — others are on your side",
 'Param Mitra':"a strongly supportive star — help and goodwill flow your way",
}

def daily_text(r):
    """Short, sweet daily reading from the computed factors."""
    lines=[]
    lines.append(STAR_MOOD[r['stars']])
    lines.append(MOON_HOUSE_LINE[r['moon_house']])
    lines.append("Today "+TARA_LINE.get(r['tara'],'the stars are mixed')+".")
    # one practical nudge based on score
    if r['stars']>=4:
        lines.append("Lean in — start things, ask for what you want, make your move.")
    elif r['stars']==3:
        lines.append("Steady as you go; nothing demands caution, nothing guarantees ease.")
    else:
        lines.append("Hold back on big decisions; tend to routine and protect your energy.")
    return " ".join(lines)

def monthly_reading(natal_moon_lon, natal_asc_lon, md_lord, year=None, month=None):
    """A month's overview: average daily energy + the best and hardest dates."""
    FLG=_setup()
    now=datetime.now()
    y=year or now.year; m=month or now.month
    # iterate days of the month
    import calendar
    ndays=calendar.monthrange(y,m)[1]
    days=[]
    for dd in range(1,ndays+1):
        r=daily_reading(natal_moon_lon,natal_asc_lon,md_lord,datetime(y,m,dd))
        days.append((dd,r['stars'],r['score'],r['tara']))
    avg=sum(d[2] for d in days)/len(days)
    best=sorted(days,key=lambda d:-d[2])[:4]
    hard=sorted(days,key=lambda d:d[2])[:3]
    avg_stars=max(1,min(5,round(3+avg*0.55)))
    monthname=calendar.month_name[m]
    return {
        'month':monthname,'year':y,'avg_stars':avg_stars,
        'best_days':sorted([d[0] for d in best]),
        'hard_days':sorted([d[0] for d in hard]),
        'best_detail':best,'hard_detail':hard
    }

def monthly_text(mr, md_lord):
    bd=', '.join(f"the {_ord(d)}" for d in mr['best_days'])
    hd=', '.join(f"the {_ord(d)}" for d in mr['hard_days'])
    txt=(f"{mr['month']} {mr['year']} carries an overall energy of {mr['avg_stars']} out of 5 for you, "
         f"read from how this month's planets move against your birth Moon while your {md_lord} period runs. ")
    txt+=(f"Your most favourable days look to be {bd} — good windows for important steps, decisions, and putting yourself forward. ")
    txt+=(f"Take a little more care around {hd}, when the transits are less smooth — better for routine and patience than big moves. ")
    txt+=("Use the daily reading each morning for the finer detail; this is the shape of the month as a whole.")
    return txt

def _ord(n):
    if 10<=n%100<=20: s='th'
    else: s={1:'st',2:'nd',3:'rd'}.get(n%10,'th')
    return f"{n}{s}"

