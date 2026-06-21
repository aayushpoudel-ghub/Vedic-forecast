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

# Openers by overall stars — sets the mood of the day
OPENER={
 5:["Today is one of those days where things just go your way.",
    "The wind is at your back today — make the most of it.",
    "A genuinely lucky day is lining up for you."],
 4:["Today leans in your favour — a good day overall.",
    "Things should flow fairly smoothly for you today.",
    "A positive day is shaping up — use the good energy."],
 3:["Today is steady — no big highs, no big lows.",
    "An ordinary, balanced day lies ahead.",
    "Today asks you to keep things ticking along quietly."],
 2:["Today may feel a little heavier than usual — go gently.",
    "Some friction is likely today; don't force things.",
    "A slightly tricky day — patience will get you through."],
 1:["Today is a demanding one — take it slow and protect your peace.",
    "A challenging day; keep your head down and avoid big risks.",
    "Today tests you a little — rest, and don't push hard."],
}

# Love line by love_stars
LOVE={
 5:"Your love life is glowing today. If you're with someone, expect real warmth, closeness, and maybe a moment that reminds you why you're together. If you're single, the energy is magnetic — don't be surprised if someone takes notice, and don't be shy about putting yourself out there.",
 4:"Romance is favoured today. It's a good time to reach out to someone you care about, plan something together, or simply enjoy the people who matter to you. A small gesture of affection goes a long way right now.",
 3:"Your love life is calm and steady today — no drama, no fireworks, just easy companionship. It's a fine day to simply be present with the people you love, without needing anything more from the moment.",
 2:"Tread gently in matters of the heart today. Small misunderstandings can spark more easily than usual, so listen more than you speak, and don't read too much into a passing mood — yours or theirs.",
 1:"Your relationships need patience today. Tempers may run short and feelings bruise easily, so avoid arguments, hold off on serious conversations, and don't make any emotional decisions you might look back on with regret.",
}
MONEY={
 5:"Money matters look bright today. Keep your eyes open — an opportunity, a useful conversation, or even a small unexpected gain could come your way. If you've been waiting for a good moment to act on something financial, this is one.",
 4:"A good day for your finances. It's favourable for earning, planning, or making a sensible purchase you've thought through. Your judgement around money is sound today, so trust it.",
 3:"Your finances are steady today — nothing to worry about, nothing that demands action. A quiet day to simply keep things ticking along and avoid unnecessary spending.",
 2:"Keep a watchful eye on money today. It's not the day for big purchases, risky bets, or financial decisions made in a hurry. If something can wait, let it wait.",
 1:"Be careful with money today. Steer well clear of loans, gambling, and any deal that sounds too good to be true. Protect what you have rather than reaching for more.",
}
WORK={
 5:"Work flows beautifully today. It's a strong day to push a project forward, ask for something you want, or simply show what you're capable of — people are more likely to notice and respond well. Make your move.",
 4:"A productive day at work is on the cards. You'll get things done, and your efforts are likely to be seen and appreciated. A good day to take initiative on something that matters to you.",
 3:"Work ticks along normally today. Handle what's in front of you, keep steady, and you'll end the day with a quiet sense of having done enough. No need to force anything.",
 2:"Work may feel like an uphill climb today. Focus on finishing what's already on your plate rather than starting something new, and be patient with colleagues who aren't quite on your wavelength.",
 1:"Work could test your patience today. Expect a few delays or obstacles, keep your cool when things don't go to plan, and resist taking on more than you can realistically manage.",
}
MOOD={
 5:"Your energy and spirits are high today. You'll feel light, capable, and ready to take on whatever comes — exactly the kind of day to make the most of how good you feel.",
 4:"You're in good spirits today. A positive, steady frame of mind carries you through, and you'll find it easier than usual to stay upbeat even if small things go sideways.",
 3:"Your mood is even and settled today — neither soaring nor sinking, just steadily yourself. A grounded day to simply get on with things.",
 2:"You may feel a little low or restless today. Be gentle with yourself, don't overthink things, and give yourself permission to rest if you need it. It's a passing cloud, not the weather.",
 1:"Your energy dips today, and you may feel more sensitive or worn than usual. Rest where you can, go easy on yourself, and don't take on anything that drains you further. Tomorrow will feel lighter.",
}
# A closing nudge by overall
CLOSER={
 5:"Bottom line: seize the day — this is a make-your-move kind of day.",
 4:"Bottom line: a good day to take a small step toward something you want.",
 3:"Bottom line: keep steady and let the day unfold naturally.",
 2:"Bottom line: play it safe today and save big decisions for another time.",
 1:"Bottom line: rest, protect your energy, and wait for a brighter day to act.",
}

def _pick(lst, seed):
    return lst[seed % len(lst)]

def daily_text(r):
    """6-7 lines, plain language, spicy, area-specific, detailed. No jargon."""
    seed = int(r['date'].replace('-',''))
    lines=[]
    lines.append(_pick(OPENER[r['stars']], seed))
    # personalized highlight: name the standout (best or worst) area of the day
    areas={'love':r['love_stars'],'money':r['money_stars'],'work':r['work_stars'],'mood':r['mood_stars']}
    best_area=max(areas,key=areas.get); worst_area=min(areas,key=areas.get)
    label={'love':'your love life','money':'your finances','work':'your work','mood':'your energy'}
    if areas[best_area]>=4 and areas[best_area]-areas[worst_area]>=2:
        lines.append(f"The standout today is <b>{label[best_area]}</b> — that's where the day really opens up for you, so put your attention there.")
    elif areas[worst_area]<=2 and areas[best_area]-areas[worst_area]>=2:
        lines.append(f"The one thing to keep an eye on today is <b>{label[worst_area]}</b> — give that part of life a little extra care and the rest of the day flows fine.")
    lines.append(LOVE[r['love_stars']])
    lines.append(MONEY[r['money_stars']])
    lines.append(WORK[r['work_stars']])
    lines.append(MOOD[r['mood_stars']])
    lines.append(CLOSER[r['stars']])
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
 5:"This is a beautiful month for love. If you're in a relationship, it deepens and feels more secure; if you're single, someone genuinely significant could come into your life, so stay open and say yes to invitations.",
 4:"Romance is on the rise this month — a warm, promising time for your relationships. Existing bonds grow closer, and there's real potential for new connection if you're looking.",
 3:"Your love life stays steady and comfortable this month. No storms, no surprises — just quiet companionship and the easy presence of the people who matter to you.",
 2:"Love asks for patience this month. There may be a few bumps or misunderstandings, so keep communication clear and honest, and try not to jump to conclusions when things feel uncertain.",
 1:"Be gentle in love this month, as relationships may hit a rough patch. Avoid ultimatums and big confrontations, give each other room to breathe, and trust that the strain will ease with time.",
}
MONTH_MONEY={
 5:"Money flows well this month. It's a strong period for income, and there's a real chance of a gain, a raise, or an opportunity you shouldn't let slip — keep your eyes open and act when the moment comes.",
 4:"Finances look healthy this month — a good time to earn, save, and make a sensible investment. Your money sense is sound, so it's a fine stretch to plan ahead.",
 3:"Your finances hold steady this month. Things stay manageable and calm, with no major swings either way — a good time to simply maintain and avoid unnecessary risk.",
 2:"Keep a close eye on money this month. Avoid big spending and don't lend what you can't comfortably spare; it's a stretch for caution rather than bold financial moves.",
 1:"Be financially careful this month. Steer clear of risky deals, loans, and large purchases, and focus on protecting what you have. This isn't the time to gamble on anything.",
}
MONTH_WORK={
 5:"Your career takes off this month — a powerful time for recognition, progress, or a real step up. Put yourself forward boldly, because your efforts are far more likely than usual to be seen and rewarded.",
 4:"Work goes well this month. It's productive and rewarding, with good chances to shine and be noticed by the people who matter. A strong month to take initiative.",
 3:"Work stays on an even keel this month — steady, reliable progress through consistent effort. Nothing dramatic, but you'll end the month having moved things meaningfully forward.",
 2:"Work may feel demanding this month. Push through patiently, focus on what you can control, and don't take on more than you can handle — it's a month for steady effort, not heroics.",
 1:"A challenging month at work, with delays and pressure more likely than usual. Focus on finishing rather than starting, keep calm under stress, and remember that this heavier stretch is temporary.",
}

def monthly_text(mr, md_lord):
    """A full, flowing paragraph — plain language, area-specific, engaging."""
    parts=[]
    # opening by overall
    o=mr['avg_stars']
    if o>=4: parts.append(f"{mr['month']} is shaping up to be a genuinely good month for you.")
    elif o==3: parts.append(f"{mr['month']} looks like a balanced, steady month overall.")
    else: parts.append(f"{mr['month']} may test you in places, so it's a month to move carefully.")
    # the three areas people care about
    parts.append(MONTH_LOVE[mr['love_stars']])
    parts.append(MONTH_MONEY[mr['money_stars']])
    parts.append(MONTH_WORK[mr['work_stars']])
    # best/worst days woven in plainly
    bd=', '.join(_ord(d) for d in mr['best_days'])
    hd=', '.join(_ord(d) for d in mr['hard_days'])
    parts.append(f"Your luckiest days this month fall around {bd} — use them for anything important. "
                 f"Take a little more care around {hd}, when things may feel heavier.")
    # a hook to keep them coming back
    parts.append("Check in each morning for your daily reading — that's where you'll catch the day-to-day shifts this overview can't show.")
    return " ".join(parts)

def _ord(n):
    if 10<=n%100<=20: s='th'
    else: s={1:'st',2:'nd',3:'rd'}.get(n%10,'th')
    return f"the {n}{s}"
