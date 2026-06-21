"""Divisional charts (vargas) — 'zoom lenses' on specific life areas.
D9 (Navamsa) = marriage, dharma, inner strength of planets.
D10 (Dasamsa) = career, profession, public life.
Returns sign placements + readable notes."""

SIGNS=['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']

def navamsa_sign(lon):
    """D9: each sign's 30° split into 9 parts of 3°20'."""
    return int(lon // (360/108)) % 12

def dasamsa_sign(lon):
    """D10: each sign split into 10 parts of 3°. Odd signs start from same sign, even from 9th."""
    sign = int(lon//30)
    part = int((lon % 30) // 3)  # 0..9
    if sign % 2 == 0:  # odd sign (0-indexed even = Aries, Gemini...)
        start = sign
    else:              # even sign: start from 9th sign
        start = (sign + 8) % 12
    return (start + part) % 12

def compute_divisionals(chart):
    P=chart['planets']
    out={'D9':{}, 'D10':{}}
    # need raw longitudes — stored as 'lon' in planets (may have been popped); recompute from sign+deg
    for nm,p in P.items():
        lon = p.get('lon')
        if lon is None:
            lon = p['sign_idx']*30 + p['deg']
        out['D9'][nm]=SIGNS[navamsa_sign(lon)]
        out['D10'][nm]=SIGNS[dasamsa_sign(lon)]
    # D9 ascendant
    asc_lon=chart['ascendant'].get('lon', chart['ascendant']['sign_idx']*30+chart['ascendant']['deg'])
    out['D9_asc']=SIGNS[navamsa_sign(asc_lon)]
    out['D10_asc']=SIGNS[dasamsa_sign(asc_lon)]

    # Vargottama detection: same sign in D1 and D9 = a major strength
    vargottama=[]
    for nm,p in P.items():
        if p['sign']==out['D9'][nm]:
            vargottama.append(nm)
    out['vargottama']=vargottama

    # D10 strength of career significators: where do Sun, Saturn, 10th-lord land in D10
    out['notes']=_divisional_notes(chart, out)
    return out

def _divisional_notes(chart, dv):
    notes=[]
    P=chart['planets']
    # Vargottama planets
    if dv['vargottama']:
        names=', '.join(dv['vargottama'])
        notes.append({'area':'strength',
            'text':f"{names} {'is' if len(dv['vargottama'])==1 else 'are'} <b>vargottama</b> — occupying the same sign in both your birth chart and your D9 navamsa. This is a notable source of strength and stability: whatever {'this planet' if len(dv['vargottama'])==1 else 'these planets'} governs tends to hold firm and deliver reliably across your life."})
    # D9 ascendant ruler note (marriage/dharma lens)
    notes.append({'area':'marriage',
        'text':f"In your D9 chart — the lens for marriage and inner life — the ascendant falls in <b>{dv['D9_asc']}</b>, colouring the deeper nature of your partnerships and the strength your planets express in close relationships."})
    # D10 career lens
    notes.append({'area':'career',
        'text':f"In your D10 chart — the lens for career and public life — the ascendant falls in <b>{dv['D10_asc']}</b>, and your Sun (vocation, authority) sits in <b>{dv['D10']['Sun']}</b>, suggesting the deeper character of your professional path beyond what the birth chart alone shows."})
    return notes

if __name__=='__main__':
    import engine
    c=engine.compute_chart(1995,12,6,22,0,26.6483,85.80,5.75)
    dv=compute_divisionals(c)
    print("D9 (Navamsa) ascendant:", dv['D9_asc'])
    print("D10 (Dasamsa) ascendant:", dv['D10_asc'])
    print("Vargottama planets:", dv['vargottama'])
    print("\nD9 placements:", dv['D9'])
    print("\nNotes:")
    for n in dv['notes']:
        print(f"  [{n['area']}] {n['text'].replace('<b>','').replace('</b>','')}")
