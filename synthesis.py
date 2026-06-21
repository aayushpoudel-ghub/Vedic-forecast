"""The master layer: convergence analysis.
A master doesn't list indicators — they count how many INDEPENDENT testimonies
point to the same conclusion, weigh them by planetary strength, and resolve
contradictions. This module produces weighted verdicts per life-area."""

def lords_for_lagna(asc_idx):
    rulers=['Mars','Venus','Mercury','Moon','Sun','Mercury','Venus','Mars','Jupiter','Saturn','Saturn','Jupiter']
    return {h: rulers[(asc_idx+h-1)%12] for h in range(1,13)}

NAT_KARAKA={  # natural significator of each life area
 'career':['Sun','Saturn','Mercury'],'wealth':['Jupiter','Venus'],
 'marriage':['Venus','Jupiter'],'health':['Sun','Moon'],
 'children':['Jupiter'],'education':['Mercury','Jupiter']}

AREA_HOUSES={'career':[10,6,11],'wealth':[2,11,5,9],'marriage':[7,2],
 'health':[1,6,8],'children':[5],'education':[4,5]}

def house_verdict(chart, strength, house_num):
    """Read ONE house three ways (lord, occupants, karaka) and combine — master style."""
    P=chart['planets']
    asc_idx=chart['ascendant']['sign_idx']
    lords=lords_for_lagna(asc_idx)
    testimonies=[]; score=0.0

    # 1. the house LORD's strength and placement
    lord=lords[house_num]; lp=P[lord]
    lord_str=strength.get(lord,{}).get('score',3)
    placed=lp['house']
    if placed in (1,4,5,7,9,10,11): score+=1; testimonies.append(f"its ruler {lord} is well-placed")
    elif placed in (6,8,12): score-=0.8; testimonies.append(f"its ruler {lord} sits in a difficult house")
    score += (lord_str-4)*0.3
    if lord_str>=5.5: testimonies.append(f"{lord} is strong")
    elif lord_str<3: testimonies.append(f"{lord} is weak, which undercuts the house")

    # 2. OCCUPANTS of the house
    occ=[nm for nm,p in P.items() if p['house']==house_num]
    for o in occ:
        if o in ('Jupiter','Venus','Mercury','Moon'):
            score+=0.7; testimonies.append(f"benefic {o} occupies it")
        elif o in ('Sun','Mars','Saturn','Rahu','Ketu'):
            score-=0.3; testimonies.append(f"{o} occupies it (intensifying but testing)")

    return {'score':round(score,2),'testimonies':testimonies,'lord':lord,'occupants':occ}

def area_analysis(chart, strength, area):
    """Combine all houses + karakas for a life area into a weighted, convergent verdict."""
    P=chart['planets']
    houses=AREA_HOUSES[area]
    karakas=NAT_KARAKA[area]
    total=0.0; all_test=[]; supports=0; challenges=0

    for h in houses:
        hv=house_verdict(chart, strength, h)
        weight=1.0 if h==houses[0] else 0.6  # primary house weighted most
        total+=hv['score']*weight
        for t in hv['testimonies']:
            all_test.append((h,t))
            if any(w in t for w in ['well-placed','strong','benefic']): supports+=1
            if any(w in t for w in ['difficult','weak','testing']): challenges+=1

    # karaka strength
    k_scores=[strength.get(k,{}).get('score',3) for k in karakas]
    k_avg=sum(k_scores)/len(k_scores)
    total+=(k_avg-4)*0.5
    if k_avg>=5.5: supports+=1; all_test.append((0,f"the natural significator ({'/'.join(karakas)}) is strong"))
    elif k_avg<3: challenges+=1; all_test.append((0,f"the natural significator ({'/'.join(karakas)}) is weak"))

    # convergence verdict
    if total>=2.5: verdict='very strong'; conf='high'
    elif total>=1: verdict='strong'; conf='good'
    elif total>=-0.5: verdict='mixed'; conf='moderate'
    elif total>=-2: verdict='challenged'; conf='good'
    else: verdict='difficult'; conf='high'

    return {'area':area,'score':round(total,2),'verdict':verdict,'confidence':conf,
            'supports':supports,'challenges':challenges,'testimonies':all_test,
            'karaka_strength':round(k_avg,2)}

def full_synthesis(chart, strength):
    """Master-style read across all major life areas with convergence."""
    return {area:area_analysis(chart, strength, area)
            for area in ['career','wealth','marriage','health','education']}

if __name__=='__main__':
    import engine, strength as st_mod
    c=engine.compute_chart(1995,12,6,22,0,26.6483,85.80,5.75)
    st=st_mod.planet_strength(c)
    syn=full_synthesis(c, st)
    print("MASTER-STYLE CONVERGENCE ANALYSIS:\n")
    for area,a in syn.items():
        print(f"{area.upper()}: {a['verdict']} (confidence: {a['confidence']})")
        print(f"  Score {a['score']} | {a['supports']} supporting vs {a['challenges']} challenging testimonies")
        key=[t for _,t in a['testimonies'][:3]]
        print(f"  Key: {'; '.join(key)}")
        print()
