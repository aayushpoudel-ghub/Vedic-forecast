"""Finer timing: pratyantardasha (3rd dasha level) for precise current sub-sub-period,
and all slow-planet transits (Saturn, Jupiter, Rahu, Ketu) relative to natal Moon/lagna."""
import swisseph as swe
from datetime import datetime, timedelta

SIGNS=['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']
DASHA_ORDER=['Ketu','Venus','Sun','Moon','Mars','Rahu','Jupiter','Saturn','Mercury']
DASHA_YEARS={'Ketu':7,'Venus':20,'Sun':6,'Moon':10,'Mars':7,'Rahu':18,'Jupiter':16,'Saturn':19,'Mercury':17}
Y=365.25

def current_pratyantardasha(chart):
    """Find the running mahadasha -> antardasha -> pratyantardasha right now."""
    now=datetime.now()
    mds=chart['mahadashas_full']
    # parse into datetimes
    def pd(s): return datetime.strptime(s,'%Y-%m-%d')
    cur_md=None
    for m in mds:
        if pd(m['start'])<=now<pd(m['end']): cur_md=m; break
    if not cur_md: return None
    # antardashas
    md_lord=cur_md['lord']; md_start=pd(cur_md['start']); tot=DASHA_YEARS[md_lord]
    sub=md_start; cur_ad=None
    for k in range(9):
        al=DASHA_ORDER[(DASHA_ORDER.index(md_lord)+k)%9]
        dur=DASHA_YEARS[al]*tot/120.0
        se=sub+timedelta(days=dur*Y)
        if sub<=now<se: cur_ad=(al,sub,se,dur); break
        sub=se
    if not cur_ad: return None
    al,ad_start,ad_end,ad_dur=cur_ad
    # pratyantardashas within current antardasha
    sub=ad_start; cur_pd=None
    for k in range(9):
        pl=DASHA_ORDER[(DASHA_ORDER.index(al)+k)%9]
        dur=DASHA_YEARS[pl]*ad_dur/120.0
        se=sub+timedelta(days=dur*Y)
        if sub<=now<se: cur_pd=(pl,sub,se); break
        sub=se
    return {'md':md_lord,'ad':al,'pd':cur_pd[0] if cur_pd else None,
            'pd_start':cur_pd[1].strftime('%Y-%m-%d') if cur_pd else None,
            'pd_end':cur_pd[2].strftime('%Y-%m-%d') if cur_pd else None}

def slow_transits(chart):
    """Saturn, Jupiter, Rahu, Ketu transit houses from natal Moon and lagna."""
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    FLG=swe.FLG_SWIEPH|swe.FLG_SIDEREAL
    now=datetime.now()
    jd=swe.julday(now.year,now.month,now.day,12)
    moon_sign=chart['planets']['Moon']['sign_idx']
    asc_sign=chart['ascendant']['sign_idx']
    out={}
    for nm,pid in [('Saturn',swe.SATURN),('Jupiter',swe.JUPITER),('Rahu',swe.MEAN_NODE)]:
        lon=swe.calc_ut(jd,pid,FLG)[0][0]
        sign=int(lon//30)
        out[nm]={'sign':SIGNS[sign],
                 'house_from_moon':((sign-moon_sign)%12)+1,
                 'house_from_lagna':((sign-asc_sign)%12)+1}
    # Ketu opposite Rahu
    rahu_sign=SIGNS.index(out['Rahu']['sign'])
    ketu_sign=(rahu_sign+6)%12
    out['Ketu']={'sign':SIGNS[ketu_sign],
                 'house_from_moon':((ketu_sign-moon_sign)%12)+1,
                 'house_from_lagna':((ketu_sign-asc_sign)%12)+1}
    return out

if __name__=='__main__':
    import engine
    c=engine.compute_chart(1995,12,6,22,0,26.6483,85.80,5.75)
    p=current_pratyantardasha(c)
    print("Current 3-level dasha:", p['md'],"->",p['ad'],"->",p['pd'])
    print("  pratyantardasha runs:", p['pd_start'],"to",p['pd_end'])
    print("\nSlow transits now:")
    for nm,t in slow_transits(c).items():
        print(f"  {nm}: in {t['sign']} — {t['house_from_lagna']}th from lagna, {t['house_from_moon']}th from Moon")
