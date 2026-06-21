"""Rich rule-based interpretation: substantial paragraphs + a year-by-year 5-year timeline.
Free, offline, deterministic. Weighted toward career, wealth, and timing."""

SIGNS=['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']

HOUSE_THEME={
 1:'your identity, body, vitality and the overall direction of life',
 2:'wealth you accumulate, family, speech, and what you value',
 3:'courage, initiative, communication, siblings, and short journeys',
 4:'home, mother, property, vehicles, and inner emotional security',
 5:'intelligence, education, creativity, romance, and children',
 6:'work and service, competition, daily routine, health, and overcoming obstacles',
 7:'partnership, marriage, business alliances, and dealings with others',
 8:'transformation, research, shared and inherited resources, and longevity',
 9:'fortune, higher learning, long journeys, faith, and the father',
 10:'career, public standing, authority, and your work in the world',
 11:'gains, income, networks, elder siblings, and the fulfilment of desires',
 12:'foreign lands, expenditure, retreat, spirituality, and what is left behind',
}

# A fuller character of each planet as a period ruler — career/wealth flavored
DASHA_LONG={
 'Sun':"The Sun's period turns life toward identity, authority, recognition, and visibility. It favours dealings with government, institutions, and those in power, and tends to bring matters of reputation and the father to the foreground. It is shorter (6 years) and more intense than soft — a time of being seen and tested on who you are, rather than a gentle drift.",
 'Moon':"The Moon's period softens and emotionalises life, turning it toward home, the mother, the public, and the mind. It favours nurturing work, the public-facing professions, and anything involving care or the broad public. Moods rise and fall more visibly, and wellbeing becomes closely tied to one's sense of belonging and emotional security.",
 'Mars':"Mars' period injects drive, ambition, competition, and physical and technical energy. It favours engineering, machines, defence, sport, surgery, and any field where one out-works or out-fights a hard problem. It rewards courage and decisive action, but asks for care with anger, haste, and conflict.",
 'Mercury':"Mercury's period turns life toward intellect, communication, commerce, and skill. It favours writing, teaching, analysis, trade, technology, and anything requiring a quick and precise mind. It tends to be busy and mentally active, with many threads running at once, and rewards adaptability and clear thinking.",
 'Jupiter':"Jupiter's period — sixteen years, the great expansive cycle — turns life toward wisdom, growth, fortune, teaching, and wealth. It favours advisory and knowledge-based work, higher study, finance, law, and anything that grows through trust and reputation. It is broadly the most benevolent of the periods, expanding whatever it touches and rewarding ethical, considered effort.",
 'Venus':"Venus' period — twenty years, the longest cycle — turns life toward relationships, comfort, beauty, art, and material ease. It favours creative fields, design, luxury, hospitality, and partnership-based work. It tends to be the most pleasant of the periods, softening hardship and drawing comfort and refinement, though it can incline toward indulgence.",
 'Saturn':"Saturn's period — nineteen years — turns life toward discipline, structure, hard sustained work, and slow maturation. It favours long-horizon building, research, infrastructure, law, and any field that rewards patience and endurance. It rarely hands quick wins, but what is built under it tends to last; it is the great teacher, rewarding integrity and punishing shortcuts.",
 'Rahu':"Rahu's period — eighteen years — turns life toward ambition, the unconventional, the foreign, and the sudden. It favours technology, research, anything cutting-edge or boundary-crossing, and dealings with foreign lands and large systems. It can bring dramatic rises and unexpected turns, rewarding boldness but asking for care against over-reach and illusion.",
 'Ketu':"Ketu's period — seven years — turns life inward, toward detachment, research, specialisation, and the spiritual. It favours deep focused expertise, investigation, healing, and contemplative or technical mastery rather than worldly visibility. It is the most psychologically demanding of the periods, often stripping away what is not essential, but it can awaken real depth and self-knowledge.",
}

DASHA_SHORT={
 'Sun':'identity and recognition','Moon':'emotional life and home','Mars':'drive and competition',
 'Mercury':'intellect and communication','Jupiter':'expansion and fortune','Venus':'comfort and relationship',
 'Saturn':'discipline and structure','Rahu':'ambition and the unconventional','Ketu':'detachment and depth'}

GEMS={'Sun':('Ruby','the Sun'),'Moon':('Pearl','the Moon'),'Mars':('Red Coral','Mars'),
 'Mercury':('Emerald','Mercury'),'Jupiter':('Yellow Sapphire','Jupiter'),
 'Venus':('Diamond or White Sapphire','Venus'),'Saturn':('Blue Sapphire','Saturn'),
 'Rahu':('Hessonite','Rahu'),'Ketu':("Cat's Eye",'Ketu')}

MANTRA={'Sun':'Om Hraam Hreem Hraum Sah Suryaya Namah (Sundays at sunrise)',
 'Moon':'Om Shraam Shreem Shraum Sah Chandraya Namah (Mondays)',
 'Mars':'Om Kraam Kreem Kraum Sah Bhaumaya Namah, and Hanuman Chalisa (Tuesdays)',
 'Mercury':'Om Braam Breem Braum Sah Budhaya Namah (Wednesdays)',
 'Jupiter':'Om Graam Greem Graum Sah Gurave Namah (Thursdays)',
 'Venus':'Om Draam Dreem Draum Sah Shukraya Namah (Fridays)',
 'Saturn':'Om Praam Preem Praum Sah Shanaye Namah, and Hanuman Chalisa (Saturdays)',
 'Rahu':'Om Bhraam Bhreem Bhraum Sah Rahave Namah (Saturdays)',
 'Ketu':'Om Sraam Sreem Sraum Sah Ketave Namah, with Ganesha worship (Tuesdays)'}

def lords_for_lagna(asc_idx):
    rulers=['Mars','Venus','Mercury','Moon','Sun','Mercury','Venus','Mars','Jupiter','Saturn','Saturn','Jupiter']
    return {h: rulers[(asc_idx+h-1)%12] for h in range(1,13)}

def _dignity_phrase(p):
    d=p.get('dignity','')
    if d=='Exalted': return ' — and here it is exalted, at its absolute strongest, a major asset in your chart'
    if d=='Own sign': return ' — and here it sits in its own sign, dignified and reliably able to deliver its results'
    if d=='Debilitated': return ' — though here it is debilitated, weakened, asking for conscious support and care'
    return ''

def interpret(chart):
    asc_idx=chart['ascendant']['sign_idx']
    lords=lords_for_lagna(asc_idx)
    P=chart['planets']
    md=chart['current_mahadasha']; ad=chart['current_antardasha']
    s={}

    # compute depth layers
    try:
        import yogas as _yogas
        chart_yogas=_yogas.detect_yogas(chart)
    except Exception:
        chart_yogas=[]
    try:
        import divisional as _div
        divs=_div.compute_divisionals(chart)
    except Exception:
        divs=None
    try:
        import timing as _tim
        praty=_tim.current_pratyantardasha(chart)
    except Exception:
        praty=None
    try:
        import strength as _str
        pstrength=_str.planet_strength(chart)
    except Exception:
        pstrength={}
    try:
        import synthesis as _syn
        convergence=_syn.full_synthesis(chart, pstrength) if pstrength else None
    except Exception:
        convergence=None

    # ---------- FOUNDATION ----------
    moon=P['Moon']; asc=chart['ascendant']
    found=(f"You are born with <b>{asc['sign']} rising</b> ({asc['deg']}°, {asc['nakshatra']} nakshatra) — "
        f"this is the lens through which your whole life is coloured, governing {HOUSE_THEME[1]}. "
        f"Your Moon, which in Vedic astrology carries the mind and emotional nature, sits in <b>{moon['sign']}</b> "
        f"in the {_ord(moon['house'])} house ({moon['nakshatra']}){_dignity_phrase(moon)}. "
        f"This shapes how you feel, react, and seek security: your inner life is bound up with {HOUSE_THEME[moon['house']]}.")
    # ascendant lord
    asc_lord=lords[1]; al=P[asc_lord]
    found+=(f" Your chart ruler is <b>{asc_lord}</b>, placed in the {_ord(al['house'])} house in {al['sign']}{_dignity_phrase(al)} — "
        f"so a great deal of your life's energy flows toward {HOUSE_THEME[al['house']]}.")
    s['foundation']=found

    # ---------- THE CURRENT PERIOD ----------
    md_p=P.get(md); md_rules=[h for h,l in lords.items() if l==md]
    period=(f"You are currently in the <b>{md} mahā­daśā</b> ({chart['md_start']} to {chart['md_end']}), "
        f"with the <b>{ad} antar­daśā</b> running inside it now. {DASHA_LONG[md]}")
    if md_p:
        period+=(f"<br><br>In your specific chart, the {md} that rules these years sits in your "
            f"<b>{_ord(md_p['house'])} house</b> in {md_p['sign']}{_dignity_phrase(md_p)}, "
            f"and rules your {_houses_list(md_rules)}. This is the crucial detail: it means the {DASHA_SHORT[md]} "
            f"this whole period brings is directed especially toward {HOUSE_THEME[md_p['house']]}"
            f"{_and_rules(md_rules)}. ")
    if md!=ad:
        ad_p=P.get(ad)
        if ad_p:
            period+=(f"The {ad} sub-period layered on top of it for now adds a flavour of {DASHA_SHORT[ad]}, "
                f"colouring the present months through its placement in your {_ord(ad_p['house'])} house.")
    if praty and praty.get('pd'):
        period+=(f"<br><br>Drilling down to the finest level, you are right now in the "
            f"<b>{praty['md']}–{praty['ad']}–{praty['pd']}</b> sub-sub-period "
            f"({praty['pd_start']} to {praty['pd_end']}), which sets the precise tone of these particular weeks.")
    s['period']=period

    # ---------- YOGAS (the headline combinations) ----------
    if chart_yogas:
        strong=[y for y in chart_yogas if y.get('strength')=='strong']
        ytext="Your chart carries several <b>yogas</b> — special planetary combinations that the tradition reads as defining features of a life. "
        if strong:
            ytext+="The most powerful in your chart: "
            ytext+=" ".join(f"<b>{y['name']}.</b> {y['meaning']}" for y in strong)
            others=[y for y in chart_yogas if y.get('strength')!='strong']
            if others:
                ytext+="<br><br>Other notable combinations: "
                ytext+=" ".join(f"<b>{y['name']}.</b> {y['meaning']}" for y in others)
        else:
            ytext+=" ".join(f"<b>{y['name']}.</b> {y['meaning']}" for y in chart_yogas)
        s['yogas']=ytext

    # ---------- DEEPER CHART (divisionals) ----------
    if divs and divs.get('notes'):
        dtext="Beyond the birth chart, Vedic astrology uses <b>divisional charts</b> — finer lenses that zoom into specific areas of life. "
        dtext+=" ".join(n['text'] for n in divs['notes'])
        s['deeper']=dtext

    # ---------- MASTER SYNTHESIS (convergence + strength) ----------
    if convergence and pstrength:
        # strongest & weakest planets frame the whole reading
        ranked=sorted(pstrength.items(), key=lambda x:-x[1]['score'])
        strongest=ranked[0]; weakest=ranked[-1]
        syn_text=(f"Reading your chart as a whole — weighing which planets are powerful and which are weak, "
            f"and counting how many independent indicators point the same way — a clearer picture emerges than any single placement gives. "
            f"<br><br>Your <b>strongest planet is {strongest[0]}</b> ({strongest[1]['verdict']}), which means the matters it governs "
            f"tend to carry through with real force in your life. Your <b>weakest is {weakest[0]}</b> ({weakest[1]['verdict']}), "
            f"the area that most needs conscious support and care. ")
        # area verdicts, ordered strongest-first
        area_order=sorted(convergence.items(), key=lambda x:-x[1]['score'])
        verdicts=[]
        for area,a in area_order:
            label={'career':'Career','wealth':'Wealth','marriage':'Marriage & partnership',
                   'health':'Health','education':'Learning'}[area]
            verdicts.append(f"<b>{label}: {a['verdict']}</b> ({a['supports']} factors support it, {a['challenges']} challenge it)")
        syn_text+="<br><br>Weighing all the indicators together, here is how the major areas of life stand in your chart: "+"; ".join(verdicts)+". "
        syn_text+="Where an area shows as 'mixed', it means your chart holds genuine tension there — real strengths pulling against real challenges — and the outcome depends more on your own choices than on destiny alone."
        s['synthesis']=syn_text

    # ---------- CAREER (deep) ----------
    tenth_lord=lords[10]; tl=P[tenth_lord]
    tenth_sign=SIGNS[(asc_idx+9)%12]
    car=(f"Your career is read first from the <b>10th house</b> — for {asc['sign']} rising this is <b>{tenth_sign}</b>, "
        f"and its lord is <b>{tenth_lord}</b>, placed in your {_ord(tl['house'])} house in {tl['sign']}{_dignity_phrase(tl)}. "
        f"This is the spine of your professional life: it suggests a vocation connected to {HOUSE_THEME[tl['house']]}, "
        f"carrying the character of {tenth_lord}. ")
    # planets in 10th
    in_tenth=[nm for nm,p in P.items() if p['house']==10]
    if in_tenth:
        car+=(f"Sitting in the 10th house itself {_isare(in_tenth)} <b>{_join(in_tenth)}</b>, "
            f"which press their nature directly onto your career and public image. ")
    # Saturn (karaka of career) condition
    sat=P['Saturn']
    car+=(f"Saturn, the natural significator of career and disciplined work, sits in your {_ord(sat['house'])} house "
        f"in {sat['sign']}{_dignity_phrase(sat)} — colouring the texture of your working life. ")
    # how the mahadasha bears on career
    if md_p:
        if md_p['house'] in (10,6,11,2,1):
            car+=(f"<br><br>Importantly, your current {md} period strongly activates the working/earning side of life "
                f"(through its placement in your {_ord(md_p['house'])} house), so these are years when professional "
                f"matters are genuinely live and movement is supported. ")
        else:
            car+=(f"<br><br>Your current {md} period works on career more indirectly — its main emphasis is on "
                f"{HOUSE_THEME[md_p['house']]} — so professional growth in these years comes as much through that "
                f"channel as through direct career push. ")
    # direction by 10th lord sign element
    # ---- weave relevant yogas into career & wealth ----
    career_yogas=[y for y in chart_yogas if y['domain'] in ('career','identity')]
    if career_yogas:
        car+="<br><br><b>Special combinations in your chart affecting career:</b> "
        car+=" ".join(f"<b>{y['name']}.</b> {y['meaning']}" for y in career_yogas)
    s['career']=car

    # ---------- WEALTH (deep) ----------
    l2=lords[2]; l11=lords[11]; p2=P[l2]; p11=P[l11]
    wealth=(f"Wealth in your chart is read mainly from two houses: the <b>2nd</b> (accumulated wealth, savings, family money) "
        f"and the <b>11th</b> (income, gains, and the fulfilment of desires). "
        f"Your 2nd lord is <b>{l2}</b> in your {_ord(p2['house'])} house in {p2['sign']}{_dignity_phrase(p2)}; "
        f"your 11th lord of gains is <b>{l11}</b> in your {_ord(p11['house'])} house in {p11['sign']}{_dignity_phrase(p11)}. ")
    # Jupiter & Venus as dhana karakas
    jup=P['Jupiter']; ven=P['Venus']
    wealth+=(f"Jupiter and Venus, the natural significators of wealth, sit respectively in your "
        f"{_ord(jup['house'])} house ({jup['sign']}{_dignity_phrase(jup)}) and your "
        f"{_ord(ven['house'])} house ({ven['sign']}{_dignity_phrase(ven)}). ")
    # exalted/own wealth signals
    signals=[]
    if jup.get('dignity') in('Exalted','Own sign') and jup['house'] in(2,5,9,11,1):
        signals.append("a strong, well-placed Jupiter is a durable foundation for abundance")
    if P['Moon'].get('dignity')=='Exalted' and P['Moon']['house'] in(2,11):
        signals.append("your exalted Moon in a wealth house is an especially strong, steady gains indicator")
    if p11.get('dignity') in('Exalted','Own sign'):
        signals.append(f"a dignified 11th lord points to reliable, growing income")
    if any(P[x]['house']==8 and x in('Rahu',) for x in P):
        signals.append("Rahu's presence in the 8th asks for real care with debt, speculation, and others' money — gains can be erratic")
    if signals:
        wealth+="<br><br>Notable signals: "+_join_sent(signals)+". "
    wealth+=_wealth_style(md, P)
    wealth_yogas=[y for y in chart_yogas if y['domain'] in ('wealth','fortune')]
    if wealth_yogas:
        wealth+="<br><br><b>Special combinations affecting your wealth and fortune:</b> "
        wealth+=" ".join(f"<b>{y['name']}.</b> {y['meaning']}" for y in wealth_yogas)
    s['wealth']=wealth

    # ---------- RELATIONSHIPS ----------
    l7=lords[7]; p7=P[l7]; dk=chart['darakaraka']
    seventh_sign=SIGNS[(asc_idx+6)%12]
    rel=(f"Partnership is read from the <b>7th house</b> — for you <b>{seventh_sign}</b> — whose lord <b>{l7}</b> "
        f"sits in your {_ord(p7['house'])} house in {p7['sign']}{_dignity_phrase(p7)}. "
        f"Your <b>Dārākaraka</b> (the planet that signifies the spouse in Jaimini astrology) is <b>{dk}</b>, "
        f"which suggests a partner whose nature carries qualities of {DASHA_SHORT[dk]}. ")
    in_seventh=[nm for nm,p in P.items() if p['house']==7]
    if in_seventh:
        rel+=f"Planets falling in your 7th house — {_join(in_seventh)} — shape the partnership directly. "
    else:
        rel+="With no planets in the 7th house itself, partnership is read mainly through its lord and the Dārākaraka above. "
    s['relationships']=rel

    # ---------- HEALTH ----------
    health=(f"Health is read from the ascendant and its lord, the 6th house of illness, and the Moon. "
        f"Your chart ruler {asc_lord} in the {_ord(al['house'])} house and your {asc['sign']} constitution set the baseline. ")
    if chart['sade_sati']:
        health+=(f"<br><br>You are currently in <b>Sade Sati</b> — Saturn transiting the {chart['sade_sati_phase']} relative to your Moon. "
            f"This roughly seven-and-a-half year passage is traditionally the most testing for mood, energy, and stamina, "
            f"and asks especially for attention to rest, mental health, routine, and not running the body down. "
            f"It is demanding but maturing, and it lifts in time. ")
    else:
        health+=(f"You are not currently in Sade Sati, which removes one of the heavier traditional pressures on wellbeing in this window. ")
    health+=("In general, guard the areas your Moon sign and Saturn govern, keep routine and sleep steady through the "
        "more intense sub-periods named in the timeline, and treat persistent low mood as a signal to seek support — "
        "the harder periods are time-bound and do pass.")
    s['health']=health

    # ---------- REMEDIES ----------
    gem,planet=GEMS[md]
    rem=(f"For your current <b>{md} mahā­daśā</b>, the traditionally indicated gemstone is <b>{gem}</b>, "
        f"worn to strengthen {planet}, the ruler of these sixteen-or-fewer years. ")
    if md in('Saturn','Rahu','Ketu'):
        rem+=(f"This is a powerful, fast-acting stone and should always be <b>trial-worn for a few days first</b> and "
            f"fitted only under an experienced astrologer's guidance — never worn casually. ")
    else:
        rem+="As with any gemstone, have it properly tested and fitted before wearing. "
    rem+=(f"<br><br>The mantra for this period is <b>{MANTRA[md]}</b>, ideally recited 108 times on its planetary day. "
        f"Beyond ritual, the most effective remedy for {md} is to live in harmony with its nature — "
        f"{_remedy_action(md)}. Gemstones for Saturn, Rahu, and Ketu (Blue Sapphire, Hessonite, Cat's Eye) "
        f"should never be worn without expert in-person assessment.")
    s['remedies']=rem

    # ---------- THE 5-YEAR TIMELINE ----------
    s['timeline']=_build_timeline(chart, lords, P)

    return s

# ---------- timeline builder ----------
def _build_timeline(chart, lords, P):
    """Year-by-year narrative driven by the antardasha sequence + Jupiter/Saturn transits."""
    items=[]
    for seg in chart['timeline']:
        md=seg['md']; ad=seg['ad']
        sy=seg['start'][:7]; ey=seg['end'][:7]
        ad_p=P.get(ad)
        rules=[h for h,l in lords.items() if l==ad]
        house=ad_p['house'] if ad_p else None
        txt=f"<b>{_month(sy)} – {_month(ey)} · {md}–{ad} period.</b> "
        txt+=f"This sub-period carries the flavour of {DASHA_SHORT[ad]}. "
        if house:
            txt+=(f"With {ad} placed in your {_ord(house)} house (ruling your {_houses_list(rules)}), "
                f"it activates {HOUSE_THEME[house]}. ")
            txt+=_subperiod_advice(md, ad, house)
        items.append(txt)
    # frame with transits
    head=(f"Across these five years your major period is <b>{chart['current_mahadasha']}</b>, and the sub-periods below "
        f"mark the chapters within it. Two slow transits shape the backdrop: <b>Saturn</b> is currently moving through "
        f"your {_ord(chart['saturn_house'])} house ({chart['saturn_transit_sign']}), and <b>Jupiter</b> through your "
        f"{_ord(chart['jupiter_house'])} house ({chart['jupiter_transit_sign']}). ")
    if chart['sade_sati']:
        head+=f"You are in Sade Sati ({chart['sade_sati_phase']}), which colours the earlier part of this window with extra weight that later eases. "
    return head+"<br><br>"+"<br><br>".join(items)

def _subperiod_advice(md, ad, house):
    benefic = ad in('Jupiter','Venus','Mercury','Moon')
    malefic = ad in('Saturn','Mars','Rahu','Ketu','Sun')
    if house in(10,6,11,2):
        if benefic: return "This is a constructive window for career and earning — favourable for advancement, new roles, or growing income; press forward."
        return "Career and money are strongly active but the going is effortful — expect hard work and tests; consolidate rather than gamble, and avoid speculation."
    if house in(1,5,9):
        if benefic: return "A genuinely favourable, fortunate stretch — good for new beginnings, learning, recognition, and overall momentum."
        return "An active period for self and fortune, but one that asks for discipline and patience; steady effort is rewarded, haste is not."
    if house in(4,):
        return "Focus turns toward home, property, family, and inner security — a period for settling and tending the foundations of life."
    if house in(7,):
        return "Partnership and dealings with others come forward — significant for relationships, marriage, and alliances."
    if house in(8,12):
        if malefic: return "A more inward, testing window — guard against losses and upheaval, avoid risk, and use it for research, rest, or quiet consolidation rather than bold moves."
        return "An inward, transformative stretch — better for depth, healing, and behind-the-scenes work than for public pushes."
    if house in(3,):
        return "A period favouring initiative, communication, short journeys, and courageous effort — good for putting yourself forward."
    return "A mixed period; follow the general nature of the sub-period ruler."

def _career_direction(tenth_lord, tl, P):
    fire=['Aries','Leo','Sagittarius']; earth=['Taurus','Virgo','Capricorn']
    air=['Gemini','Libra','Aquarius']; water=['Cancer','Scorpio','Pisces']
    sign=tl['sign']
    base="<br><br><b>Direction:</b> "
    by_planet={
     'Sun':'government, administration, leadership, medicine, or positions of authority',
     'Moon':'the public, care professions, hospitality, food, travel, or work with the broad public',
     'Mars':'engineering, technology, machines, defence, surgery, sport, or competitive technical work',
     'Mercury':'analysis, writing, technology, trade, finance, teaching, or communication',
     'Jupiter':'advisory and knowledge work, teaching, law, finance, or anything growing through trust and wisdom',
     'Venus':'creative and design fields, the arts, luxury, hospitality, or partnership-based work',
     'Saturn':'long-horizon technical or structural work, research, law, infrastructure, or service in large institutions',
     'Rahu':'technology, research, foreign or cutting-edge fields, and unconventional or boundary-crossing work',
     'Ketu':'deep specialist expertise, research, healing, or technical mastery away from the spotlight',
    }
    return base+f"With {tenth_lord} ruling your career, your professional nature leans toward {by_planet.get(tenth_lord,'varied fields')}. This is reinforced by where it sits and the houses it touches."

def _wealth_style(md, P):
    base="<br><br><b>How wealth tends to come for you:</b> "
    if md=='Jupiter': return base+"under Jupiter, wealth grows through reputation, knowledge, and ethical expansion — steadily and durably, rewarding patience over speculation. These are good years to build income and let it compound."
    if md=='Saturn': return base+"under Saturn, wealth comes slowly and through sustained effort and structure — not windfalls, but what is built holds. Conservative saving suits this period far better than risk."
    if md=='Venus': return base+"under Venus, wealth flows with relative ease, often through relationships, creative or comfort-related work, and partnership; the main risk is over-indulgence rather than scarcity."
    if md=='Mercury': return base+"under Mercury, wealth comes through skill, commerce, communication, and many small streams rather than one — adaptability and trade favour you."
    if md=='Sun': return base+"under the Sun, wealth is tied to status, authority, and recognition — gains follow standing and position more than speculation."
    if md=='Moon': return base+"under the Moon, income can ebb and flow with circumstance and mood; steadier when tied to the public or to nurturing work."
    if md=='Mars': return base+"under Mars, wealth comes through drive, technical skill, and competition — earned actively; guard against impulsive financial decisions."
    if md=='Rahu': return base+"under Rahu, wealth can rise dramatically and unconventionally, but unpredictably — avoid speculation and leverage, which this period makes genuinely dangerous."
    if md=='Ketu': return base+"under Ketu, material focus is weaker and gains can be irregular, often through unconventional channels — a period to keep finances conservative and simple."
    return base+"follow the nature of the period ruler."

def _remedy_action(md):
    return {
     'Sun':'honour discipline and integrity, respect father-figures and authority, and offer water to the rising Sun',
     'Moon':'protect emotional balance and sleep, honour the mother, and keep a steady, nurturing routine',
     'Mars':'channel energy into physical exercise and disciplined effort, and guard against anger and haste',
     'Mercury':'keep the mind active and honest, study, and communicate with care and clarity',
     'Jupiter':'act with ethics and generosity, pursue knowledge, honour teachers, and give to worthy causes',
     'Venus':'cultivate beauty, harmony, and devotion in relationships, while avoiding over-indulgence',
     'Saturn':'embrace discipline and patience, serve elders and labourers, keep commitments scrupulously, and donate on Saturdays',
     'Rahu':'stay grounded and honest, avoid shortcuts and illusions, and serve the marginalised',
     'Ketu':'turn inward through meditation and spiritual practice, honour Ganesha, and pursue depth over display',
    }.get(md,'live in harmony with the period')

# ---------- small helpers ----------
def _ord(n):
    return {1:'1st',2:'2nd',3:'3rd',4:'4th',5:'5th',6:'6th',7:'7th',8:'8th',9:'9th',10:'10th',11:'11th',12:'12th'}[n]
def _houses_list(hs):
    if not hs: return 'no houses'
    return ' and '.join(_ord(h) for h in hs)+(' house' if len(hs)==1 else ' houses')
def _and_rules(hs):
    if not hs: return ''
    return f", and toward the affairs of your {_houses_list(hs)}"
def _join(lst):
    if len(lst)==1: return lst[0]
    if len(lst)==2: return f"{lst[0]} and {lst[1]}"
    return ', '.join(lst[:-1])+f", and {lst[-1]}"
def _join_sent(lst):
    return _join(lst)
def _isare(lst): return 'is' if len(lst)==1 else 'are'
def _month(ym):
    y,m=ym.split('-'); names=['','January','February','March','April','May','June','July','August','September','October','November','December']
    return f"{names[int(m)]} {y}"

if __name__=='__main__':
    import engine
    c=engine.compute_chart(1995,12,6,22,0,26.6483,85.80,5.75)
    s=interpret(c)
    for k in ['foundation','period','career','wealth','timeline','remedies']:
        print(f"\n{'='*60}\n[{k.upper()}]\n{'='*60}")
        print(s[k].replace('<br>','\n').replace('<b>','').replace('</b>',''))
