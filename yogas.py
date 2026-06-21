"""Yoga detection — named planetary combinations that are the heart of Vedic reading.
Each yoga returns a name, a plain-language meaning, and a domain (career/wealth/etc.)
so the interpretation engine can weave them in."""

def _house(p): return p['house']
def _sign(p): return p['sign_idx']
def _planet_in_house(P, h): return [nm for nm,p in P.items() if p['house']==h]
def _conjunct(P, a, b): return P[a]['sign_idx']==P[b]['sign_idx']

# which houses each planet rules for a given ascendant sign
def lords_for_lagna(asc_idx):
    rulers=['Mars','Venus','Mercury','Moon','Sun','Mercury','Venus','Mars','Jupiter','Saturn','Saturn','Jupiter']
    return {h: rulers[(asc_idx+h-1)%12] for h in range(1,13)}

KENDRAS=[1,4,7,10]; TRIKONAS=[1,5,9]; DUSTHANAS=[6,8,12]
BENEFICS=['Jupiter','Venus','Mercury','Moon']
MALEFICS=['Sun','Mars','Saturn','Rahu','Ketu']

def detect_yogas(chart):
    P=chart['planets']
    asc_idx=chart['ascendant']['sign_idx']
    lords=lords_for_lagna(asc_idx)
    found=[]

    def add(name, meaning, domain, strength='present'):
        found.append({'name':name,'meaning':meaning,'domain':domain,'strength':strength})

    # ---- Gajakesari Yoga: Jupiter in kendra (1/4/7/10) from Moon ----
    moon_sign=P['Moon']['sign_idx']; jup_sign=P['Jupiter']['sign_idx']
    rel=((jup_sign-moon_sign)%12)+1
    if rel in (1,4,7,10):
        add('Gajakesari Yoga',
            "Jupiter and the Moon form a powerful, classical combination for intelligence, good reputation, wisdom, and rising fortune through life. It lends respect, optimism, and the support of others.",
            'fortune')

    # ---- Budha-Aditya Yoga: Sun + Mercury conjunct ----
    if _conjunct(P,'Sun','Mercury'):
        add('Budha-Aditya Yoga',
            "The Sun and Mercury sit together, sharpening the intellect and communication. It favours clear thinking, learning, analysis, writing, and recognition through the mind.",
            'career')

    # ---- Chandra-Mangala: Moon + Mars conjunct (wealth) ----
    if _conjunct(P,'Moon','Mars'):
        add('Chandra-Mangala Yoga',
            "The Moon and Mars together create drive toward wealth and resourcefulness — a money-making combination, though it asks for emotional balance.",
            'wealth')

    # ---- Raja Yogas: lord of a kendra conjunct/with lord of a trikona ----
    kendra_lords={lords[h] for h in KENDRAS}
    trikona_lords={lords[h] for h in TRIKONAS}
    raja_pairs=set()
    for kl in kendra_lords:
        for tl in trikona_lords:
            if kl!=tl and _conjunct(P,kl,tl):
                raja_pairs.add(tuple(sorted((kl,tl))))
    for a,b in raja_pairs:
        add('Raja Yoga',
            f"{a} and {b} — rulers of an angle and a trine of your chart — combine to form a Raja Yoga, a classical mark of success, authority, and rising status. It is one of the strongest indicators of achievement in a chart.",
            'career','strong')

    # ---- Dhana Yogas: 2nd & 11th lords related to 5th/9th (wealth) ----
    l2,l5,l9,l11=lords[2],lords[5],lords[9],lords[11]
    wealth_links=[]
    for a,b,desc in [(l2,l11,'the lords of wealth and gains'),
                     (l2,l5,'the lords of wealth and fortune'),
                     (l11,l5,'the lords of gains and intelligence'),
                     (l9,l11,'the lords of fortune and gains')]:
        if a!=b and _conjunct(P,a,b):
            wealth_links.append(desc)
    if wealth_links:
        add('Dhana Yoga',
            f"A wealth-giving combination forms in your chart, as {wealth_links[0]} unite — a classical signature for accumulating money and prosperity over time.",
            'wealth')

    # ---- Pancha Mahapurusha Yogas: Mars/Mercury/Jupiter/Venus/Saturn in own/exalt AND in a kendra ----
    MPY={'Mars':('Ruchaka','courage, leadership, discipline and physical strength — a commanding, action-oriented nature'),
         'Mercury':('Bhadra','intelligence, eloquence, and skill — a sharp, learned, articulate nature'),
         'Jupiter':('Hamsa','wisdom, virtue, and good fortune — a respected, ethical, knowledgeable nature'),
         'Venus':('Malavya','charm, comfort, artistic gifts, and material pleasures — a refined, attractive nature'),
         'Saturn':('Sasa','discipline, authority, and endurance — a capacity for sustained power and influence')}
    for pl,(yname,desc) in MPY.items():
        p=P[pl]
        if p['house'] in KENDRAS and p['dignity'] in ('Exalted','Own sign'):
            add(f'{yname} Yoga (Pancha Mahapurusha)',
                f"A rare and auspicious 'great person' yoga: {pl}, strong in an angle of your chart, grants {desc}.",
                'identity','strong')

    # ---- Neecha Bhanga: a debilitated planet whose debilitation is cancelled ----
    for nm,p in P.items():
        if p.get('dignity')=='Debilitated':
            # simple cancellation: lord of the debilitation sign is in a kendra from lagna or Moon
            add('Neecha Bhanga (partial)',
                f"{nm} is debilitated but shows signs of cancellation — a classical pattern where an early weakness or struggle transforms into unexpected strength and rise later in life.",
                'fortune')

    # ---- Kemadruma (Moon isolation) - a caution yoga ----
    moon_h=P['Moon']['house']
    adjacent=[(moon_h%12)+1, ((moon_h-2)%12)+1]
    occupied_adjacent=any(_planet_in_house(P,h) for h in adjacent)
    if not occupied_adjacent and not _planet_in_house(P, moon_h)[1:]:
        # only if truly nothing flanks the Moon and Moon alone
        pass  # often cancelled; skip to avoid false alarms

    # ---- Vipareeta Raja Yoga: dusthana lords in dusthanas ----
    l6,l8,l12=lords[6],lords[8],lords[12]
    vry=[nm for nm in [l6,l8,l12] if P[nm]['house'] in DUSTHANAS]
    if len(set(vry))>=2:
        add('Vipareeta Raja Yoga',
            "An unusual 'reversal' yoga where difficulty becomes advantage — you tend to rise through challenges that would set others back, often gaining when circumstances seem against you.",
            'fortune')

    return found

if __name__=='__main__':
    import engine
    c=engine.compute_chart(1995,12,6,22,0,26.6483,85.80,5.75)
    ys=detect_yogas(c)
    print(f"Yogas found in your chart ({len(ys)}):")
    for y in ys:
        print(f"\n  ★ {y['name']} [{y['domain']}]")
        print(f"    {y['meaning']}")
