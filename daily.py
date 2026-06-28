"""Daily & monthly personalized readings from real transits.
Plain-language, life-area-specific, no jargon in the output.
Star rating + per-area scores (love, money, work, mood) are computed, not random."""
import swisseph as swe
from datetime import datetime, timedelta
import calendar

SIGNS=['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']
NAKS=['Ashwini','Bharani','Krittika','Rohini','Mrigashira','Ardra','Punarvasu','Pushya','Ashlesha','Magha','P.Phalguni','U.Phalguni','Hasta','Chitra','Swati','Vishakha','Anuradha','Jyeshtha','Mula','P.Ashadha','U.Ashadha','Shravana','Dhanishta','Shatabhisha','P.Bhadrapada','U.Bhadrapada','Revati']

def _setup():
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    return swe.FLG_SWIEPH | swe.FLG_SIDEREAL

GOCHARA_GOOD={
 'Sun':[3,6,10,11],'Moon':[1,3,6,7,10,11],'Mars':[3,6,11],'Mercury':[2,4,6,8,10,11],
 'Jupiter':[2,5,7,9,11],'Venus':[1,2,3,4,5,8,9,11,12],'Saturn':[3,6,11],
 'Rahu':[3,6,11],'Ketu':[3,6,11]}

TARA_QUALITY=[('Janma',0),('Sampat',1),('Vipat',-1),('Kshema',1),('Pratyak',-1),
 ('Sadhana',1),('Naidhana',-1),('Mitra',1),('Param Mitra',1)]

def positions(jd, FLG):
    out={}
    for nm,pid in [('Sun',swe.SUN),('Moon',swe.MOON),('Mars',swe.MARS),('Mercury',swe.MERCURY),
                   ('Jupiter',swe.JUPITER),('Venus',swe.VENUS),('Saturn',swe.SATURN)]:
        out[nm]=swe.calc_ut(jd,pid,FLG)[0][0]
    r=swe.calc_ut(jd,swe.MEAN_NODE,FLG)[0][0]
    out['Rahu']=r; out['Ketu']=(r+180)%360
    return out

def _house_from(planet_lon, moon_sign):
    return ((int(planet_lon//30) - moon_sign) % 12) + 1

def compute_day(natal_moon_lon, md_lord, d, ad_lord=None):
    """Core computation: overall + per-area scores for one day.
    ad_lord (antardasha lord), if given, adds finer accuracy."""
    FLG=_setup()
    jd = swe.julday(d.year, d.month, d.day, 6.0)
    pos = positions(jd, FLG)
    nms = int(natal_moon_lon//30)               # natal moon sign
    nmn = int(natal_moon_lon//(360/27))         # natal moon nakshatra
    dmn = int(pos['Moon']//(360/27))            # day moon nakshatra
    dms = int(pos['Moon']//30)

    # overall via Tara + Moon gochara + benefic/malefic + dasha lords
    overall=0.0
    tara_idx=(dmn-nmn)%9; tname,tq=TARA_QUALITY[tara_idx]; overall+=tq*1.5
    moon_h=_house_from(pos['Moon'],nms); overall+=(1.0 if moon_h in GOCHARA_GOOD['Moon'] else -0.7)
    for ben in ['Jupiter','Venus']:
        h=_house_from(pos[ben],nms); overall+=(0.7 if h in GOCHARA_GOOD[ben] else -0.3)
    for mal in ['Saturn','Mars']:
        h=_house_from(pos[mal],nms); overall+=(0.5 if h in GOCHARA_GOOD[mal] else -0.6)
    if md_lord in pos:
        h=_house_from(pos[md_lord],nms); overall+=(0.8 if h in GOCHARA_GOOD.get(md_lord,[3,6,11]) else -0.5)
    # finer: antardasha lord's transit adds a smaller weight
    if ad_lord and ad_lord in pos:
        h=_house_from(pos[ad_lord],nms); overall+=(0.4 if h in GOCHARA_GOOD.get(ad_lord,[3,6,11]) else -0.25)

    # ---- per-area scores ----
    # LOVE/RELATIONSHIP: Venus position + Moon house (7-ish/emotional) 
    venus_h=_house_from(pos['Venus'],nms)
    love = (1.2 if venus_h in GOCHARA_GOOD['Venus'] else -0.9)
    love += (0.6 if moon_h in [5,7,11] else (-0.5 if moon_h in [6,8,12] else 0))
    # MONEY/FINANCE: Jupiter + house 2/11 emphasis
    jup_h=_house_from(pos['Jupiter'],nms)
    money = (1.2 if jup_h in GOCHARA_GOOD['Jupiter'] else -0.7)
    money += (0.6 if moon_h in [2,11] else (-0.4 if moon_h in [8,12] else 0))
    # WORK/CAREER: Sun + Mars + Saturn (effort), house 6/10
    sun_h=_house_from(pos['Sun'],nms); mars_h=_house_from(pos['Mars'],nms); sat_h=_house_from(pos['Saturn'],nms)
    work = 0.0
    work += (0.6 if sun_h in GOCHARA_GOOD['Sun'] else -0.4)
    work += (0.5 if mars_h in GOCHARA_GOOD['Mars'] else -0.4)
    work += (0.5 if sat_h in GOCHARA_GOOD['Saturn'] else -0.5)
    work += (0.5 if moon_h in [6,10,11] else 0)
    # MOOD/ENERGY: Moon house + Tara
    mood = (1.0 if moon_h in GOCHARA_GOOD['Moon'] else -0.8) + tq*0.8

    def to5(x, spread):
        return max(1, min(5, round(3 + x*spread)))

    return {
        'date': d.strftime('%Y-%m-%d'),
        'overall': overall,
        'stars': to5(overall, 0.55),
        'love': love, 'love_stars': to5(love, 0.9),
        'money': money, 'money_stars': to5(money, 0.85),
        'work': work, 'work_stars': to5(work, 0.7),
        'mood': mood, 'mood_stars': to5(mood, 0.7),
        'tara': tname,
    }

# backwards-compatible wrapper
def daily_reading(natal_moon_lon, natal_asc_lon, md_lord, target_date=None):
    d = target_date or datetime.now()
    return compute_day(natal_moon_lon, md_lord, d)


# ============ PLAIN-LANGUAGE, SPICY TEXT LAYER ============
# No astrology jargon in output. People want WHAT, not WHY.
# Quirky-best-friend voice. Each slot has MULTIPLE variants so it rotates daily
# and the joke never gets stale. Selected by date-seed (stable within a day).

# Openers by overall stars
OPENER={
 5:["Okay, today is straight-up golden — the universe is basically rolling out the red carpet for you.",
    "Spoiler alert: today's got serious main-character energy. Go be iconic.",
    "Today is one of those days where everything just *clicks*. Ride the wave.",
    "Look, the cosmos pulled some strings for you today — this one's a total win."],
 4:["Today's giving good vibes — things should flow your way without much fuss.",
    "Solid day incoming. The universe is quietly in your corner on this one.",
    "Today leans your way — not fireworks, just smooth, easy wins.",
    "Good news: today's got your back. Lean into it."],
 3:["Today is giving 'main character on a rest day' energy — chill, drama-free, just yours.",
    "Today's a quiet one — no plot twists, no chaos, just a steady, do-your-thing kind of day.",
    "Okay, today's pretty chill. Nothing wild, nothing scary — just cruise.",
    "Today's that comfortable in-between vibe. Coast through it."],
 2:["Heads up — the universe hit the snooze button on your luck today. Go gentle.",
    "Today's a *little* spicy, and not in the fun way. Don't force anything.",
    "Okay, today's got some friction — nothing major, but don't push your luck.",
    "Today's a 'stay in your lane and drink some water' kind of day. You've got this."],
 1:["Real talk: today's a tough one. Keep your head down, protect your peace, and just get through it.",
    "Today the cosmos is clearly testing you. Survival mode is totally valid.",
    "Okay, today's rough around the edges — go slow, skip the big risks, be kind to yourself.",
    "Today's a stay-in-bed-if-you-can kind of day. No shame in playing it safe."],
}

# LOVE — now arrays per rating
LOVE={
 5:["The stars are basically playing matchmaker for you right now. Got a partner? Plan something sweet. Flying solo? Flash that smile — a tiny gesture racks up *major* points today.",
    "Your love life is straight-up glowing today. If you're coupled up, expect a swoon-worthy moment. If you're single, the energy is magnetic — don't be shy.",
    "Cupid clearly clocked in early for you today. Warmth, butterflies, the whole rom-com package — say yes to it."],
 4:["Romance is on your side today. Reach out, plan a little something, or just soak up the people you love. A small sweet gesture goes a long way.",
    "Love's got a soft glow today — a great moment to connect, text first, or be the one who makes the plan.",
    "Today's a green light for the heart. Nothing dramatic, just easy warmth — lean into it."],
 3:["Love's on cruise control today — no drama, no fireworks, just cozy and easy. Perfect for a low-key night with your person (or your dog).",
    "Your love life is chilling today. Nothing to fix, nothing to chase — just enjoy the easy company.",
    "Romance is in comfy-sweatpants mode today. Steady, calm, drama-free. Honestly? Underrated."],
 2:["Okay, tread lightly in the love department today — little misunderstandings can snowball, so listen more than you fire off texts.",
    "Hearts are a touch fragile today. Don't read into a weird mood — yours or theirs — and skip the heavy conversations.",
    "Love's a bit prickly today. Bite your tongue on the spicy comeback and you'll dodge a pointless squabble."],
 1:["Relationship red flag day — and the flag is just 'be careful.' Avoid arguments, don't make big emotional calls, and let the dust settle.",
    "The heart's running hot today, and not in a good way. Step back from any drama before it picks *you*.",
    "Today's not the day to hash out the big feelings. Tempers are short — protect your peace and revisit it later."],
}
MONEY={
 5:["Money's looking up — keep your eyes peeled, because an opportunity (or a sweet little surprise) could land. If you've been waiting for a sign to make a smart move, this is it.",
    "Your wallet's got good energy today. A useful tip, a small win, maybe an unexpected bit of cash — stay alert and say yes to the good stuff.",
    "Okay, finance vibes are *immaculate* today. The door's open — walk through it (the smart way)."],
 4:["Solid money day. Good for earning, planning, or finally buying that thing you've actually thought through. Trust your gut here.",
    "Your money sense is sharp today — a fine moment to plan, save, or make a sensible move.",
    "Finances are quietly winning today. Nothing flashy, just steady green lights."],
 3:["Money's just... fine today. Nothing scary, nothing exciting. Keep it boring and skip the impulse buys.",
    "Your finances are coasting today — steady as she goes. Maybe don't 'treat yourself' just because.",
    "Wallet's on chill mode today. No moves required — just don't go wild on the checkout page."],
 2:["Okay, let's talk wallet: keep it zipped. Not the day to fund your sudden urge for an air fryer or a risky bet. If it can wait, let it wait.",
    "Money's a little wobbly today. Big purchases? Risky bets? Hard pass. Leave it in the cart till tomorrow.",
    "Today, your credit card and you should take a little break from each other. No big spends, no gambles."],
 1:["Hide your credit card from yourself today. Seriously — no loans, no gambles, no 'too good to be true' deals. Guard what you've got.",
    "Financial danger-zone day. If it's not survival, it's a no. Protect the bag and walk away from anything shiny.",
    "Today the money gods say: do nothing risky. No deals, no big buys, no lending. Just hold steady."],
}
WORK={
 5:["Work is *chef's kiss* today. Push that project, ask for the thing, show 'em what you've got — people are watching and they'll be impressed. Make your move.",
    "Career energy is peaking today. It's your moment to shine, pitch, or level up — don't sit on it.",
    "Today work bends to your will. Big asks, bold moves, standout effort — all favored. Go get it."],
 4:["Productive-day alert: you'll get stuff done and people will actually notice. Good day to take the lead on something you care about.",
    "Work's flowing today — momentum's on your side, and your effort won't go unseen.",
    "Solid day at work incoming. Tackle the good stuff and enjoy the 'I'm on a roll' feeling."],
 3:["Work's coasting on autopilot today. Just handle what's in front of you, don't reinvent the wheel, and you'll log off feeling like you actually got things done.",
    "Career mode: cruise control. Knock out your tasks, keep it steady, call it a win.",
    "Work's pretty low-key today. No need to be a hero — just do the thing and clock out satisfied."],
 2:["Work might feel like wading through syrup today. Finish what's already on your plate instead of starting new chaos, and be patient with the slow folks.",
    "Today work's a bit of an uphill walk. Keep your head down, wrap up loose ends, and don't pile on more.",
    "Okay, work's testing you today. Lower the bar to 'finish what exists' and you'll be fine."],
 1:["Work's in gremlin mode today — expect delays and hiccups. Keep your cool, don't take on extra, and just ride it out.",
    "Career chaos day. Stuff will go sideways; your superpower today is staying calm and not biting back.",
    "Today work fights you at every turn. Survival, not heroics — finish the bare minimum and let it go."],
}
MOOD={
 5:["You're radiating today — light, confident, ready for anything. This is your 'unstoppable' face. Wear it.",
    "Your energy is *peak* today. You feel good, you look good, you've got this. Soak it up.",
    "Main-character mood fully activated today. High energy, good vibes — go enjoy being you."],
 4:["You're in genuinely good spirits today — upbeat and steady, and small annoyances bounce right off you.",
    "Good-mood day. You've got that easy, light feeling that makes everything smoother.",
    "Your vibe is solidly positive today. Ride that good energy."],
 3:["Your mood's perfectly chilled — not flying too high, not sinking low. Just a solid, drama-free day to be you.",
    "Emotionally, you're on an even keel today. Steady, grounded, nothing to overthink.",
    "Today you're just... fine, in the best way. Calm, settled, no rollercoaster. Enjoy the flat road."],
 2:["You might feel a little 'meh' or restless today — totally normal. Be soft with yourself and don't spiral over small stuff. It's a passing cloud.",
    "Energy's a touch low today. Go gentle, skip the overthinking, and rest if you need to. This mood is temporary.",
    "Today's a bit of an emotional grey-sky day. Don't fight it — just be kind to yourself and wait for the sun."],
 1:["Running on empty today, and feeling everything a little too much. Rest where you can, go easy on yourself — tomorrow genuinely feels lighter.",
    "Low-battery day for the soul. Be extra gentle with yourself and don't take on anything draining.",
    "Today your energy dips and feelings run big. That's okay. Rest, breathe, and let yourself off the hook."],
}
# Closers by overall
CLOSER={
 5:["Bottom line: this is a make-your-move day. Go be the main character.",
    "TL;DR: the stars are showing off for you — don't waste it.",
    "Bottom line: seize it. Days like this don't knock twice."],
 4:["Bottom line: take one small step toward something you want today. Momentum loves you right now.",
    "TL;DR: good day to be a little brave. Go for it.",
    "Bottom line: the door's open a crack — give it a push."],
 3:["Bottom line: keep it steady and let the day do its thing. No forcing required.",
    "TL;DR: cruise, don't sprint. Today's a coasting day.",
    "Bottom line: just be you and let it flow. Easy does it."],
 2:["Bottom line: play it safe and save the big stuff for a brighter day.",
    "TL;DR: today's a 'stay in your lane' day. That's a strategy, not a cop-out.",
    "Bottom line: low stakes only today. Be patient — better days are coming."],
 1:["Bottom line: rest, guard your energy, and wait this one out. You'll bounce back.",
    "TL;DR: survival mode is the move today. Be kind to yourself.",
    "Bottom line: do nothing risky, drink some water, and let tomorrow be the comeback."],
}

def _pick(lst, seed):
    return lst[seed % len(lst)] if isinstance(lst,list) else lst

def daily_text(r):
    """6-7 lines, quirky best-friend voice, area-specific. Variants rotate by date."""
    seed = int(r['date'].replace('-',''))
    lines=[]
    lines.append(_pick(OPENER[r['stars']], seed))
    # personalized standout callout (rotate the phrasing too)
    areas={'love':r['love_stars'],'money':r['money_stars'],'work':r['work_stars'],'mood':r['mood_stars']}
    best_area=max(areas,key=areas.get); worst_area=min(areas,key=areas.get)
    label={'love':'your love life','money':'your wallet','work':'your work','mood':'your energy'}
    STANDOUT_GOOD=[
      f"Today's MVP? <b>{label[best_area]}</b> — that's where the magic's happening, so put your energy there.",
      f"The glow-up zone today is <b>{label[best_area]}</b> — lean all the way in.",
      f"If you do one thing today, lean into <b>{label[best_area]}</b> — that's where you're winning."]
    STANDOUT_WATCH=[
      f"The one thing to side-eye today? <b>{label[worst_area]}</b> — give it a little extra TLC and the rest flows fine.",
      f"Keep one eye on <b>{label[worst_area]}</b> today — handle it gently and you're golden.",
      f"Today's 'proceed with caution' sticker goes on <b>{label[worst_area]}</b>. Tread soft there."]
    if areas[best_area]>=4 and areas[best_area]-areas[worst_area]>=2:
        lines.append(_pick(STANDOUT_GOOD, seed))
    elif areas[worst_area]<=2 and areas[best_area]-areas[worst_area]>=2:
        lines.append(_pick(STANDOUT_WATCH, seed))
    lines.append(_pick(LOVE[r['love_stars']], seed))
    lines.append(_pick(MONEY[r['money_stars']], seed+1))
    lines.append(_pick(WORK[r['work_stars']], seed+2))
    lines.append(_pick(MOOD[r['mood_stars']], seed+3))
    lines.append(_pick(CLOSER[r['stars']], seed))
    return lines

# ============ MONTHLY ============
def monthly_reading(natal_moon_lon, natal_asc_lon, md_lord, year=None, month=None):
    now=datetime.now(); y=year or now.year; m=month or now.month
    ndays=calendar.monthrange(y,m)[1]
    days=[compute_day(natal_moon_lon, md_lord, datetime(y,m,dd)) for dd in range(1,ndays+1)]
    def avg(k): return sum(d[k] for d in days)/len(days)
    avgs={'overall':avg('overall'),'love':avg('love'),'money':avg('money'),'work':avg('work'),'mood':avg('mood')}
    best=sorted(days,key=lambda d:-d['overall'])[:4]
    hard=sorted(days,key=lambda d:d['overall'])[:3]
    def to5(x,s): return max(1,min(5,round(3+x*s)))
    return {
        'month':calendar.month_name[m],'year':y,
        'avg_stars':to5(avgs['overall'],0.55),
        'love_stars':to5(avgs['love'],0.9),'money_stars':to5(avgs['money'],0.85),
        'work_stars':to5(avgs['work'],0.7),'mood_stars':to5(avgs['mood'],0.7),
        'best_days':sorted([int(d['date'][-2:]) for d in best]),
        'hard_days':sorted([int(d['date'][-2:]) for d in hard]),
    }

# Monthly headline themes by area strength
MONTH_LOVE={
 5:"Love-wise? This month is a whole vibe. Coupled up — things get deeper and cozier. Single — someone genuinely worth your time could stroll in, so say yes to the invites and keep your heart open.",
 4:"Romance is trending up this month. Existing bonds get warmer, and if you're looking, there's real potential for a spark. Put yourself out there.",
 3:"Love stays comfy and low-key this month — no storms, no plot twists, just easy companionship. Sometimes drama-free is exactly the win.",
 2:"Love needs a little patience this month. A few bumps and crossed wires are likely, so keep it honest, communicate clearly, and don't spiral over small stuff.",
 1:"Heads up — love hits a bumpy patch this month. Skip the ultimatums and big confrontations, give each other breathing room, and trust that this rough stretch passes.",
}
MONTH_MONEY={
 5:"Money's looking *good* this month — strong for income, and there's a real shot at a gain, a raise, or an opportunity worth grabbing. Stay sharp and pounce when it shows up.",
 4:"Finances are healthy this month — solid for earning, saving, and making a smart, planned-out move. Your money instincts are on point.",
 3:"Money holds steady this month — calm, manageable, no wild swings. A good stretch to just maintain and resist the urge to splurge.",
 2:"Keep money on a short leash this month. Big spends and risky bets can wait — and don't lend out what you can't comfortably wave goodbye to.",
 1:"Money needs guarding this month. Steer clear of risky deals, loans, and big purchases, and focus on protecting what you've got. Not the month to gamble on anything.",
}
MONTH_WORK={
 5:"Career glow-up incoming — this month is big for recognition, progress, or a legit step up. Be bold and put yourself forward, because your effort is way more likely than usual to get noticed and rewarded.",
 4:"Work's firing on all cylinders this month — productive, rewarding, and full of chances to shine in front of the right people. Take the initiative.",
 3:"Work stays steady this month — reliable, consistent progress. Nothing flashy, but you'll close out the month having genuinely moved the needle.",
 2:"Work's a bit demanding this month. Pace yourself, focus on what you can actually control, and don't pile on more than you can carry. Steady beats heroic.",
 1:"Work's a grind this month — delays and pressure are likelier than usual. Focus on finishing over starting, keep your cool, and remember this heavier stretch is temporary.",
}

def monthly_text(mr, md_lord):
    """A full, flowing paragraph — quirky best-friend voice, area-specific, engaging."""
    parts=[]
    o=mr['avg_stars']
    if o>=4: parts.append(f"Okay, {mr['month']} is shaping up to be a genuinely great month for you — here's the scoop.")
    elif o==3: parts.append(f"{mr['month']} is looking like a steady, no-drama month overall. Here's how it breaks down.")
    else: parts.append(f"Real talk: {mr['month']} might test you in a few spots, so it's a move-smart kind of month. Here's the lay of the land.")
    parts.append(MONTH_LOVE[mr['love_stars']])
    parts.append(MONTH_MONEY[mr['money_stars']])
    parts.append(MONTH_WORK[mr['work_stars']])
    bd=', '.join(_ord(d) for d in mr['best_days'])
    hd=', '.join(_ord(d) for d in mr['hard_days'])
    parts.append(f"Mark your calendar: your luckiest days land around {bd} — that's when to make your big moves. "
                 f"And maybe tread lightly around {hd}, when things might feel a little heavier.")
    parts.append("Pro tip: check in each morning for your daily reading — that's where you'll catch the day-to-day plot twists this monthly overview can't capture.")
    return " ".join(parts)

def _ord(n):
    if 10<=n%100<=20: s='th'
    else: s={1:'st',2:'nd',3:'rd'}.get(n%10,'th')
    return f"the {n}{s}"
