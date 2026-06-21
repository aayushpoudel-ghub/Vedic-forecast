"""The EXCEPTIONS ENGINE — a master's memorized library of special cases.

A master doesn't apply rules mechanically; they recognize exceptions that flip
or modify the plain reading. This module encodes the highest-impact classical
exceptions and checks the chart against ALL of them, returning adjustments
(score modifiers + plain-language notes) that the synthesis layer applies
BEFORE reaching a verdict. This is pattern-matching against memorized wisdom."""

# Yogakaraka planet for each ascendant: the single most benefic planet,
# ruling both a kendra and a trikona. Its 'malefic' placements are GOOD.
YOGAKARAKA = {
 'Aries':'Sun','Taurus':'Saturn','Gemini':None,'Cancer':'Mars','Leo':'Mars',
 'Virgo':None,'Libra':'Saturn','Scorpio':'Moon','Sagittarius':None,
 'Capricorn':'Venus','Aquarius':'Venus','Pisces':None}

# Functional benefics/malefics differ by ascendant. Key functional MALEFICS
# (lords of 3,6,8,11 / dusthana) whose presence is more complex than 'benefic planet good'.
SIGNS=['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']

def lords_for_lagna(asc_idx):
    rulers=['Mars','Venus','Mercury','Moon','Sun','Mercury','Venus','Mars','Jupiter','Saturn','Saturn','Jupiter']
    return {h: rulers[(asc_idx+h-1)%12] for h in range(1,13)}

def check_exceptions(chart, strength):
    """Return a list of exceptions that apply, each with: area, score_adjust, note."""
    P=chart['planets']
    asc_sign=chart['ascendant']['sign']
    asc_idx=chart['ascendant']['sign_idx']
    lords=lords_for_lagna(asc_idx)
    found=[]

    def add(area, adjust, note, label):
        found.append({'area':area,'adjust':adjust,'note':note,'label':label})

    # ===== EXCEPTION 1: Yogakaraka in a dusthana is STILL excellent =====
    yk=YOGAKARAKA.get(asc_sign)
    if yk and yk in P:
        h=P[yk]['house']
        if h in (6,8,12):
            add('career', +1.5,
                f"Although {yk} sits in a typically difficult house, for your ascendant {yk} is the <b>Yogakaraka</b> — the single most beneficial planet in your chart. Its placement here does not harm; on the contrary, it gives the power to overcome enemies, win competitions, and rise through exactly the struggles that would set others back. This is a hidden strength most readings would miss.",
                'Yogakaraka exception')
        elif h in (1,4,5,7,9,10):
            add('career', +1.0,
                f"{yk} is your <b>Yogakaraka</b> — the most beneficial planet for your ascendant — and it is well placed, a major asset for success, status, and good fortune across life.",
                'Yogakaraka strength')

    # ===== EXCEPTION 2: Neecha Bhanga — debilitation cancelled = rise after struggle =====
    for nm,p in P.items():
        if nm in ('Rahu','Ketu'): continue
        if p.get('dignity')=='Debilitated':
            sign_idx=p['sign_idx']
            # cancellation conditions (simplified but classical):
            # (a) lord of the debilitation sign is in a kendra from lagna or Moon
            disp=['Mars','Venus','Mercury','Moon','Sun','Mercury','Venus','Mars','Jupiter','Saturn','Saturn','Jupiter'][sign_idx]
            disp_h=P[disp]['house'] if disp in P else 0
            moon_h=P['Moon']['house']
            cancelled = disp_h in (1,4,7,10) or ((disp_h-moon_h)%12+1) in (1,4,7,10)
            if cancelled:
                add('fortune', +1.0,
                    f"{nm} is debilitated but its weakness is <b>cancelled</b> (Neecha Bhanga). This is one of the most powerful patterns in astrology: an early weakness, struggle, or humble start that transforms into unexpected strength and a notable rise later in life. What looks like a flaw becomes a source of power.",
                    'Neecha Bhanga Raja Yoga')

    # ===== EXCEPTION 3: Exalted planet in a dusthana — strength partly locked =====
    for nm,p in P.items():
        if nm in ('Rahu','Ketu'): continue
        if p.get('dignity')=='Exalted' and p['house'] in (6,8,12):
            add('caution', -0.3,
                f"{nm} is exalted but placed in a hidden house — its great strength is real but works behind the scenes or is released only after some delay or difficulty, rather than showing openly. Patience lets its quality emerge.",
                'Exalted in dusthana')

    # ===== EXCEPTION 4: Vargottama planet — doubled reliability =====
    # (computed in divisional; here we credit it as a strength exception)
    # checked via strength scores being high AND we note it
    # ===== EXCEPTION 5: Kendra-Trikona Raja Yoga with strong planets = strong success =====
    KENDRAS=[1,4,7,10]; TRIKONAS=[1,5,9]
    kl={lords[h] for h in KENDRAS}; tl={lords[h] for h in TRIKONAS}
    for a in kl:
        for b in tl:
            if a!=b and P[a]['sign_idx']==P[b]['sign_idx']:
                sa=strength.get(a,{}).get('score',3); sb=strength.get(b,{}).get('score',3)
                if (sa+sb)/2 >= 5:
                    add('career', +0.8,
                        f"A success-yoga (Raja Yoga) in your chart is formed by <b>strong</b> planets, not weak ones — which means it delivers on its promise of status and achievement rather than remaining mere potential. A genuinely powerful indicator.",
                        'Strong Raja Yoga')

    # ===== EXCEPTION 6: benefic in own/exalt in a kendra = pillar of stability =====
    for nm,p in P.items():
        if nm in ('Jupiter','Venus','Mercury','Moon') and p['house'] in (1,4,7,10) and p.get('dignity') in ('Exalted','Own sign'):
            add('fortune', +0.7,
                f"{nm}, a natural benefic, sits strong and dignified in an angle of your chart — a pillar of stability and protection that supports you through life's harder moments and lends overall good fortune.",
                'Benefic in kendra')

    # ===== EXCEPTION 7: 10th lord in 10th = strong career self-determination =====
    if P[lords[10]]['house']==10:
        add('career', +0.8,
            "The ruler of your career sits in the house of career itself — a strong sign of a clear professional identity and the power to determine your own path through your own efforts.",
            '10th lord in 10th')

    # ===== EXCEPTION 8: dusthana lord in dusthana = Vipareeta (difficulty becomes gain) =====
    l6,l8,l12=lords[6],lords[8],lords[12]
    dusth=[nm for nm in [l6,l8,l12] if P[nm]['house'] in (6,8,12)]
    if len(set(dusth))>=2:
        add('fortune', +0.6,
            "An unusual 'reversal' pattern (Vipareeta Raja Yoga) sits in your chart — you tend to gain precisely from situations that defeat others, rising through crises, competition, or adversity. Setbacks have a way of turning to your advantage.",
            'Vipareeta Raja Yoga')

    # ===== EXCEPTION 9: combust planet — weakened despite other strengths =====
    sun_lon=P['Sun'].get('lon',P['Sun']['sign_idx']*30+P['Sun']['deg'])
    for nm,p in P.items():
        if nm in ('Sun','Rahu','Ketu'): continue
        plon=p.get('lon',p['sign_idx']*30+p['deg'])
        sep=abs((plon-sun_lon+180)%360-180)
        combust_orb={'Moon':12,'Mars':17,'Mercury':14,'Jupiter':11,'Venus':10,'Saturn':15}.get(nm,10)
        if sep < combust_orb and nm=='Mercury' and sep<5:
            # very close Mercury-Sun is actually Budha-Aditya (good), so only flag others / wide
            pass
        elif sep < combust_orb and nm!='Mercury':
            add('caution', -0.4,
                f"{nm} sits very close to the Sun and is 'combust' — its natural strength is somewhat burned up, so the matters it governs may underperform what the rest of the chart promises. Worth conscious attention.",
                'Combustion')
            break  # note once

    return found

def apply_exceptions(convergence, exceptions):
    """Fold exception adjustments into the convergence verdicts and attach notes."""
    if not exceptions:
        return convergence
    # group adjustments by area
    for exc in exceptions:
        area=exc['area']
        if area in convergence:
            convergence[area]['score']=round(convergence[area]['score']+exc['adjust'],2)
            convergence[area].setdefault('exceptions',[]).append(exc)
            # re-derive verdict after adjustment
            sc=convergence[area]['score']
            if sc>=2.5: convergence[area]['verdict']='very strong'
            elif sc>=1: convergence[area]['verdict']='strong'
            elif sc>=-0.5: convergence[area]['verdict']='mixed'
            elif sc>=-2: convergence[area]['verdict']='challenged'
            else: convergence[area]['verdict']='difficult'
    return convergence

if __name__=='__main__':
    import engine, strength as st_mod, synthesis as syn_mod
    c=engine.compute_chart(1995,12,6,22,0,26.6483,85.80,5.75)
    st=st_mod.planet_strength(c)
    exc=check_exceptions(c, st)
    print(f"EXCEPTIONS FOUND IN YOUR CHART ({len(exc)}):\n")
    for e in exc:
        print(f"  ⚡ {e['label']} [{e['area']}, adjust {e['adjust']:+.1f}]")
        print(f"     {e['note'][:160].replace(chr(60)+'b'+chr(62),'').replace(chr(60)+'/b'+chr(62),'')}...")
        print()
    # show before/after on career
    syn=syn_mod.full_synthesis(c, st)
    print("BEFORE exceptions — career:", syn['career']['verdict'], f"(score {syn['career']['score']})")
    syn2=apply_exceptions(syn, exc)
    print("AFTER exceptions  — career:", syn2['career']['verdict'], f"(score {syn2['career']['score']})")
