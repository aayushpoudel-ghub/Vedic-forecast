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
            pass
        elif sep < combust_orb and nm!='Mercury':
            add('caution', -0.4,
                f"{nm} sits very close to the Sun and is 'combust' — its natural strength is somewhat burned up, so the matters it governs may underperform what the rest of the chart promises. Worth conscious attention.",
                'Combustion')
            break

    # Helper: houses from the Moon
    moon_sign=P['Moon']['sign_idx']
    def from_moon(planet_name):
        return ((P[planet_name]['sign_idx']-moon_sign)%12)+1
    def planets_in_house_from_moon(target_h):
        return [nm for nm,p in P.items() if nm not in ('Sun','Rahu','Ketu') and ((p['sign_idx']-moon_sign)%12)+1==target_h]

    # ===== EXCEPTION 10: Dharma-Karmadhipati Yoga (9th & 10th lords united) — strongest Raja Yoga =====
    l9,l10=lords[9],lords[10]
    if l9!=l10:
        united = (P[l9]['sign_idx']==P[l10]['sign_idx'])  # conjunction
        # or mutual exchange
        exchange = (P[l9]['house']==10 and P[l10]['house']==9)
        if united or exchange:
            s9=strength.get(l9,{}).get('score',3); s10=strength.get(l10,{}).get('score',3)
            adj = 1.4 if (s9+s10)/2>=5 else 0.9
            add('career', adj,
                f"Your chart carries the <b>Dharma-Karmadhipati Yoga</b> — the union of the lords of fortune and career ({l9} and {l10}), widely considered the single most powerful success combination in Vedic astrology. It aligns your professional path with your deeper purpose and is a classical mark of those who rise to authority and high position, especially as their related periods unfold.",
                'Dharma-Karmadhipati Yoga')

    # ===== EXCEPTION 11: Lunar support yogas (Sunapha/Anapha/Durudhara) vs Kemadruma =====
    second_from_moon = planets_in_house_from_moon(2)
    twelfth_from_moon = planets_in_house_from_moon(12)
    has_2 = len(second_from_moon)>0
    has_12 = len(twelfth_from_moon)>0
    if has_2 and has_12:
        add('fortune', +0.6,
            "Your Moon is flanked by planets on both sides (<b>Durudhara Yoga</b>) — a supportive configuration that steadies the mind and tends to bring material comfort, balance, and help from others throughout life.",
            'Durudhara Yoga')
    elif has_2 or has_12:
        add('fortune', +0.3,
            f"Your Moon has planetary support beside it ({'Sunapha' if has_2 else 'Anapha'} Yoga) — lending the mind steadiness and bringing self-earned standing and resourcefulness.",
            'Lunar support yoga')
    else:
        # Kemadruma — but check the classical cancellations before flagging
        moon_h=P['Moon']['house']
        kendra_from_lagna = moon_h in (1,4,7,10)
        # benefic in kendra from Moon?
        benefic_kendra_from_moon = any(from_moon(b) in (1,4,7,10) for b in ('Jupiter','Venus','Mercury') if b in P)
        moon_dignity_ok = P['Moon'].get('dignity') in ('Exalted','Own sign')
        cancelled = kendra_from_lagna or benefic_kendra_from_moon or moon_dignity_ok
        if not cancelled:
            add('caution', -0.7,
                "Your Moon stands without planetary support on either side (<b>Kemadruma Yoga</b>), which the tradition links to periods of emotional isolation and effortful struggle, especially earlier in life. The flip side, classically noted, is that it often forges deep self-reliance and inner strength — and its weight eases as life matures.",
                'Kemadruma Yoga')
        else:
            add('fortune', +0.2,
                "Although your Moon lacks immediate planetary neighbours, the classical conditions that would make this difficult are <b>cancelled</b> in your chart — so the isolation it might bring is lifted, and the mind finds its support by other means.",
                'Kemadruma cancelled')

    # ===== EXCEPTION 12: Shakata Yoga (Jupiter in 6/8/12 from Moon) — fluctuating fortune =====
    jup_from_moon = from_moon('Jupiter')
    if jup_from_moon in (6,8,12):
        # cancelled if Jupiter is in a kendra from lagna
        if P['Jupiter']['house'] not in (1,4,7,10):
            add('caution', -0.4,
                "There is a <b>Shakata Yoga</b> in your chart (a strained angle between Jupiter and the Moon), classically linked to fortunes that rise and fall rather than climbing steadily. The lesson it carries is resilience — you regain what you lose, and learn to ride the cycles rather than fear them.",
                'Shakata Yoga')

    # ===== EXCEPTION 13: Parivartana (mutual exchange) between good houses =====
    GOOD=[1,2,4,5,7,9,10,11]
    # exchange detection: lord of h1 sits in h2, and lord of h2 sits in h1
    for h1 in range(1,13):
        a=lords[h1]
        ah=P[a]['house']
        if ah==h1: continue
        b=lords[ah]
        if b!=a and P[b]['house']==h1:
            if h1 in (1,5,9,10,11) and ah in (1,5,9,10,11):
                add('fortune', +0.7,
                    f"Two key areas of your chart are linked by a <b>mutual exchange</b> (Parivartana Yoga) between houses {min(h1,ah)} and {max(h1,ah)} — a powerful tie where each strengthens the other, weaving together the matters they govern and amplifying their results in your life.",
                    'Parivartana Yoga')
                break

    # ===== EXCEPTION 14: Saraswati Yoga (Jupiter+Venus+Mercury well placed) — learning & eloquence =====
    jvm_houses=[P['Jupiter']['house'],P['Venus']['house'],P['Mercury']['house']]
    if all(h in (1,2,4,5,7,9,10) for h in jvm_houses):
        # Mercury or Jupiter should be reasonably dignified
        if strength.get('Jupiter',{}).get('score',3)>=4 or strength.get('Mercury',{}).get('score',3)>=4:
            add('education', +0.7,
                "Your chart holds <b>Saraswati Yoga</b> — Jupiter, Venus, and Mercury all well placed together — named for the goddess of knowledge. It blesses you with intelligence, eloquence, learning, and creative or artistic gifts, and is a classical signature of writers, teachers, and articulate, cultured minds.",
                'Saraswati Yoga')

    # ===== EXCEPTION 15: Amala Yoga (benefic in 10th from lagna or Moon) — clean reputation =====
    tenth_occupants=[nm for nm,p in P.items() if p['house']==10]
    tenth_from_moon_occ = planets_in_house_from_moon(10)
    if any(b in tenth_occupants for b in ('Jupiter','Venus','Mercury')) or any(b in tenth_from_moon_occ for b in ('Jupiter','Venus','Mercury')):
        add('career', +0.6,
            "Your chart carries <b>Amala Yoga</b> — a natural benefic crowning the house of career and public life. It grants a lasting good reputation, respect that is earned cleanly, and a name that stays untarnished. People with this placement are remembered well and often drawn toward work that benefits others.",
            'Amala Yoga')

    # ===== EXCEPTION 16: Grahan (eclipse) affliction — Sun/Moon with Rahu/Ketu =====
    for luminary in ('Sun','Moon'):
        for node in ('Rahu','Ketu'):
            if P[luminary]['sign_idx']==P[node]['sign_idx']:
                area = 'caution'
                add(area, -0.4,
                    f"Your {luminary} sits with {node}, an 'eclipse' contact the tradition treats with care — it can cloud confidence and clarity ({('identity and vitality' if luminary=='Sun' else 'emotions and peace of mind')}) at times, and asks for conscious grounding. Handled with awareness, it can also lend unusual depth, intuition, and an unconventional path.",
                    'Grahan (eclipse) contact')
                break

    # ===== EXCEPTION 17: Maha Bhagya Yoga — great fortune (day/night + odd/even rule) =====
    # Needs birth time (day/night). Approx via Sun's house: Sun in houses 7-12 ~ above horizon (day)
    sun_house=P['Sun']['house']
    is_day = sun_house in (7,8,9,10,11,12)
    asc_odd = (asc_idx%2==0)  # 0-indexed even = odd sign (Aries=1st odd)
    sun_odd = (P['Sun']['sign_idx']%2==0)
    moon_odd = (P['Moon']['sign_idx']%2==0)
    if is_day and asc_odd and sun_odd and moon_odd:
        add('fortune', +0.8,
            "Your chart carries <b>Maha Bhagya Yoga</b> — the 'great fortune' combination, a rare and highly auspicious birth pattern. It is classically said to bless the person with good character, prosperity, status, and a fortunate life overall — one of the genuinely lucky configurations to be born under.",
            'Maha Bhagya Yoga')
    elif (not is_day) and (not asc_odd) and (not sun_odd) and (not moon_odd):
        add('fortune', +0.8,
            "Your chart carries <b>Maha Bhagya Yoga</b> — the 'great fortune' combination, a rare and highly auspicious birth pattern said to bless the person with good character, prosperity, status, and a fortunate life. One of the genuinely lucky configurations to be born under.",
            'Maha Bhagya Yoga')

    # ===== EXCEPTION 18: Lakshmi Yoga — 9th lord strong + Venus dignified in good house + strong lagna =====
    l9b=lords[9]
    l9_strong = strength.get(l9b,{}).get('score',3)>=5 or P[l9b].get('dignity') in ('Exalted','Own sign')
    venus_dignified = P['Venus'].get('dignity') in ('Exalted','Own sign')
    venus_good_house = P['Venus']['house'] in (1,4,5,7,9,10)
    lagna_lord_strong = strength.get(lords[1],{}).get('score',3)>=4.5
    if l9_strong and (venus_dignified and venus_good_house) and lagna_lord_strong:
        add('wealth', +1.2,
            "Your chart holds <b>Lakshmi Yoga</b> — named for the goddess of wealth, formed when the lord of fortune is strong and Venus shines dignified in a powerful house, all anchored by a strong ascendant. It is the 'queen' of wealth combinations, promising not just prosperity and comfort but a life of refinement and good fortune, typically blossoming after age 30. Wealth tends to come through honest means, and generosity comes naturally.",
            'Lakshmi Yoga')

    # ===== EXCEPTION 19: Kahala Yoga — 4th & 9th lords linked / 4th-10th lords (drive + fortune) =====
    l4=lords[4]; l10b=lords[10]
    kahala = False
    if l4!=l9b:
        rel4 = ((P[l4]['house']-P[l9b]['house'])%12)
        if rel4 in (0,3,6,9):
            kahala=True
    if l4!=l10b and P[l4]['sign_idx']==P[l10b]['sign_idx']:
        kahala=True
    if kahala and strength.get(lords[1],{}).get('score',3)>=4:
        add('career', +0.6,
            "Your chart carries <b>Kahala Yoga</b> — a tie between the houses of happiness and fortune that grants drive, boldness, and a fighting spirit. It tends to make people determined and enterprising, able to push through where others give up, and brings a measure of good luck and leadership to back that effort.",
            'Kahala Yoga')

    # ===== EXCEPTION 20: Guru-Chandala Yoga — Jupiter conjunct Rahu =====
    if P['Jupiter']['sign_idx']==P['Rahu']['sign_idx']:
        add('caution', -0.4,
            "Your chart has <b>Guru-Chandala Yoga</b> (Jupiter sitting with Rahu) — a complex contact that can scramble judgement, faith, and conventional wisdom at times, occasionally bringing unorthodox beliefs or a questioning of authority. Its higher expression, though, is genuine originality: many unconventional thinkers and reformers carry it, channeling the friction into fresh, boundary-breaking insight.",
            'Guru-Chandala Yoga')

    # ===== EXCEPTION 21: Daridra Yoga — 11th lord (income) in a dusthana =====
    l11b=lords[11]
    if P[l11b]['house'] in (6,8,12) and strength.get(l11b,{}).get('score',3) < 5:
        add('wealth', -0.6,
            "There's a classical caution in your chart around <b>income holding onto itself</b> — the ruler of gains sits in a draining house, the tradition's signature for money that tends to leak toward debts, expenses, or unexpected costs as fast as it arrives. The remedy is structural: deliberate saving, avoiding unnecessary liabilities, and building buffers. Forewarned is forearmed here.",
            'Daridra (income-drain) caution')

    # ===== EXCEPTION 22: Nodes as Yogakaraka — Rahu/Ketu in trine/quadrant with a yoga lord =====
    KEN_TRI=[1,4,5,7,9,10]
    kt_lords={lords[h] for h in (1,4,5,7,9,10)}
    for node in ('Rahu','Ketu'):
        if P[node]['house'] in KEN_TRI:
            node_with_ktlord = any(P[node]['sign_idx']==P[l]['sign_idx'] for l in kt_lords if l not in ('Rahu','Ketu'))
            if node_with_ktlord:
                add('fortune', +0.5,
                    f"In your chart {node} sits in a powerful house alongside a key chart-ruler — a special condition where this normally-disruptive shadow planet is elevated into a <b>force for success</b> (a yogakaraka). It can channel its intensity and ambition into real achievement, often through unconventional or modern paths, rather than mere turbulence.",
                    f'{node} as yogakaraka')
                break

    # ===== EXCEPTION 23: Gajakesari quality check — credit only a STRONG, unafflicted one =====
    moon_sign_b=P['Moon']['sign_idx']; jup_sign_b=P['Jupiter']['sign_idx']
    relgk=((jup_sign_b-moon_sign_b)%12)+1
    if relgk in (1,4,7,10):
        jup_afflicted = (P['Jupiter'].get('dignity')=='Debilitated'
                         or P['Jupiter']['sign_idx']==P['Rahu']['sign_idx']
                         or strength.get('Jupiter',{}).get('score',3)<3)
        if not jup_afflicted and strength.get('Jupiter',{}).get('score',3)>=5:
            add('fortune', +0.5,
                "Your <b>Gajakesari Yoga</b> (the celebrated Moon–Jupiter combination) is formed by a genuinely strong Jupiter — which means it delivers on its promise of wisdom, respect, lasting reputation, and prosperity, rather than remaining a faint potential. This is one of the more reassuring marks of a well-regarded, fortunate life.",
                'Gajakesari (strong)')

    # ===== EXCEPTION 24: Bright Moon (Poorna Chandra) — strong, benefic mind =====
    brightness = chart.get('moon_brightness', 0.5)
    waxing = chart.get('moon_waxing', True)
    if brightness >= 0.7 and waxing:
        add('fortune', +0.5,
            "You were born under a <b>bright, waxing Moon</b> — what the tradition calls a 'full' or Poorna Chandra. This is one of the quiet but genuine strengths of a chart: it lends emotional resilience, an optimistic and stable mind, natural likeability, and a steady inner foundation that carries you through hard times better than most.",
            'Bright Moon (Poorna Chandra)')
    elif brightness <= 0.25 and not waxing:
        add('caution', -0.4,
            "You were born under a <b>dark, waning Moon</b> (near the new-moon phase) — which the tradition treats with care, as it can incline the mind toward sensitivity, restlessness, or self-doubt at times. The gift hidden inside it is depth: a rich inner world and real emotional intelligence, once you learn to steady the waters. Caring for your mental wellbeing pays off especially well for you.",
            'Dark Moon (Ksheena Chandra)')

    # ===== EXCEPTION 25: Graha Yuddha (planetary war) — loser's significations weakened =====
    wars = chart.get('planetary_wars', [])
    if wars:
        w = wars[0]
        loser = w['loser']; winner = w['winner']
        # only flag if the loser is an important planet (lagna lord, or a benefic)
        is_important = (loser==lords[1]) or (loser in ('Jupiter','Venus'))
        if is_important:
            add('caution', -0.4,
                f"In your chart {loser} and {winner} sit locked in a 'planetary war' — extremely close together — and {loser} comes off the weaker of the two. The matters {loser} governs can feel like they're fighting an uphill battle or getting overshadowed, especially earlier in life. Naming it helps: with awareness, you can consciously support that area rather than let it quietly lose ground.",
                'Graha Yuddha (planetary war)')
        else:
            add('caution', -0.2,
                f"A close 'planetary war' sits in your chart between {winner} and {loser}, lending a note of inner tension between two drives — but it touches a less central part of the chart, so it colours rather than dominates.",
                'Graha Yuddha (minor)')

    # ===== EXCEPTION 26: Papa Kartari around the Moon — mind under pressure (with cancellation) =====
    if chart.get('moon_kartari') == 'papa':
        # cancelled if Moon is itself very strong / bright
        if not (brightness>=0.6 or P['Moon'].get('dignity') in ('Exalted','Own sign')):
            add('caution', -0.5,
                "Your Moon is <b>hemmed between difficult planets</b> (Papa Kartari) — a configuration the tradition links to a mind that can feel boxed-in, pressured, or caught between hard forces, particularly in younger years. The flip side is grit: people with this often develop real emotional toughness and learn to hold steady under pressure that would rattle others. Protecting your peace is genuinely worth prioritising.",
                'Papa Kartari (Moon hemmed)')
    elif chart.get('moon_kartari') == 'shubha':
        add('fortune', +0.4,
            "Your Moon is <b>cradled between gentle, benefic planets</b> (Shubha Kartari) — a lovely, protective configuration. It surrounds your inner life with support and ease, lending emotional steadiness, kindness, and a sense of being looked after by life even in harder moments.",
            'Shubha Kartari (Moon protected)')

    # ===== EXCEPTION 27: Sunapha/Anapha quality — wealth-supporting if benefics flank Moon =====
    # (the bare yogas are handled in EXC 11; here we add the WEALTH nuance when benefic)
    def from_moon_local(pn): return ((P[pn]['sign_idx']-P['Moon']['sign_idx'])%12)+1
    second_benefic = any(from_moon_local(b)==2 for b in ('Jupiter','Venus','Mercury') if b in P)
    if second_benefic and strength.get('Jupiter',{}).get('score',3)>=4:
        add('wealth', +0.4,
            "A benefic planet sits just ahead of your Moon — a classical marker (a strong Sunapha) for <b>self-made wealth and sound financial instincts</b>. You tend to build resources through your own intelligence and well-timed decisions rather than luck alone, and you're inclined to be measured and optimistic about money.",
            'Sunapha (wealth-supporting)')

    return found

def apply_exceptions(convergence, exceptions):
    """Fold exception adjustments into the convergence verdicts and attach notes.
    'fortune' exceptions lift overall fortune (spread lightly across life areas);
    'caution' exceptions register as a general note. Area-specific ones adjust that area."""
    if not exceptions:
        return convergence

    def rederive(area):
        sc=convergence[area]['score']
        if sc>=2.5: convergence[area]['verdict']='very strong'
        elif sc>=1: convergence[area]['verdict']='strong'
        elif sc>=-0.5: convergence[area]['verdict']='mixed'
        elif sc>=-2: convergence[area]['verdict']='challenged'
        else: convergence[area]['verdict']='difficult'

    for exc in exceptions:
        area=exc['area']
        if area in convergence:
            convergence[area]['score']=round(convergence[area]['score']+exc['adjust'],2)
            convergence[area].setdefault('exceptions',[]).append(exc)
            rederive(area)
        elif area=='fortune':
            # a general blessing/affliction: spread a fraction across the trine-related areas
            convergence.setdefault('_fortune',0)
            convergence['_fortune']=round(convergence.get('_fortune',0)+exc['adjust'],2)
            for a in ('career','wealth'):
                if a in convergence:
                    convergence[a]['score']=round(convergence[a]['score']+exc['adjust']*0.35,2)
                    convergence[a].setdefault('exceptions',[]).append(exc)
                    rederive(a)
        elif area=='caution':
            convergence.setdefault('_caution_notes',[]).append(exc)
            # mild general drag
            for a in ('health',):
                if a in convergence:
                    convergence[a]['score']=round(convergence[a]['score']+exc['adjust']*0.4,2)
                    rederive(a)
        elif area=='identity':
            # identity-strength yogas (e.g. Mahapurusha) lift career & overall
            if 'career' in convergence:
                convergence['career']['score']=round(convergence['career']['score']+exc['adjust']*0.5,2)
                convergence['career'].setdefault('exceptions',[]).append(exc)
                rederive('career')
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
