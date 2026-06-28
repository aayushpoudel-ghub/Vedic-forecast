"""'How your life rewards you' — the merit-vs-luck / earned-vs-sudden signature.
A master reads not just WHETHER someone succeeds, but the NATURE of it:
slow earned mastery vs sudden fortunate breaks. This is computable from the
balance of 'merit planets' vs 'sudden-change planets' weighted by strength
and house placement. Plain language, deeply personal, no jargon in output."""

# Merit / earned-through-effort signature: Saturn (discipline), Sun (authority earned),
# Jupiter (wisdom/merit), strong in houses of work(6), career(10), exams/competition(5).
# Sudden / luck / risk signature: Rahu (sudden, unconventional), Mars (bold risk),
# in houses of speculation/gambling, sudden gains, change.

EARN_HOUSES={6:1.0, 10:1.0, 5:0.7, 1:0.5, 9:0.7, 8:0.6, 4:0.4}  # where earned merit shows (8th=research/depth/effort)
LUCK_HOUSES={11:0.8, 3:0.5}                                       # pure sudden-gain houses

def reward_signature(chart, strength):
    P=chart['planets']
    asc_idx=chart['ascendant']['sign_idx']

    def s(pl): return strength.get(pl,{}).get('score',3)

    # MERIT score: discipline & earned planets, strong & in earning houses
    merit=0.0
    for pl,w in [('Saturn',1.3),('Jupiter',1.1),('Sun',0.9),('Mercury',0.7)]:
        sc=s(pl); h=P[pl]['house']
        merit += (sc-3)*0.3*w
        merit += EARN_HOUSES.get(h,0)*0.6*w
        if P[pl].get('dignity') in ('Exalted','Own sign'): merit += 0.5*w

    # LUCK score: genuinely sudden-fortune signature — primarily Rahu in gain/speculation
    luck=0.0
    # Rahu is THE sudden-luck planet; only counts when in speculative/gain houses
    rahu_h=P['Rahu']['house']
    if rahu_h in (11,5): luck += 1.2
    elif rahu_h in (3,8,1): luck += 0.5
    # Mars boldness in gain/speculation houses
    mars_h=P['Mars']['house']
    if mars_h in (11,3): luck += 0.5
    # A strong, well-placed 11th lord in a kendra = gains flow more easily (some luck)
    rulers=['Mars','Venus','Mercury','Moon','Sun','Mercury','Venus','Mars','Jupiter','Saturn','Saturn','Jupiter']
    l11=rulers[(asc_idx+10)%12]
    if P[l11]['house'] in (1,4,7,10) and s(l11)>=5: luck += 0.5
    # Venus/Moon strong in 5th (speculation side) adds a little
    for pl in ('Venus','Moon'):
        if P[pl]['house']==5 and s(pl)>=5: luck += 0.3

    merit=round(merit,2); luck=round(luck,2)
    # recenter: merit accumulates from 4 planets, so subtract a baseline to make it relative
    merit_adj = merit - 2.0
    diff=merit_adj-luck

    # Build the plain-language reading
    if diff > 0.8:
        kind='earner'
        text=("Here's something true about you: <b>you're built to earn your wins, not gamble for them.</b> "
              "Your chart rewards patience, effort, and mastery — the scholarship over the lottery, the exam passed through "
              "preparation rather than the lucky break. You may notice you rarely win things by pure chance: the raffle, the bet, "
              "the coin-flip opportunities tend to pass you by. Don't take that personally — it's simply not how your life is wired. "
              "Your luck is the slow, reliable kind that shows up <i>because</i> you put in the work. So lean into the things that reward "
              "effort and skill, and don't waste energy or money on pure gambles — they're genuinely not your lane. When you feel like "
              "the world isn't handing you easy breaks, remember: you were never meant to win that way. You're meant to earn it, and you do.")
    elif diff < -0.5:
        kind='lucky'
        text=("Here's something interesting about you: <b>your life tends to move through sudden openings and lucky breaks</b> more "
              "than slow grinding. Opportunities can appear out of nowhere, doors open unexpectedly, and you often land things through "
              "timing, boldness, or being in the right place at the right moment. The flip side: steady, repetitive effort can feel harder "
              "to sustain for you than for others. Your gift is recognising and seizing the sudden moment — so stay alert for those windows, "
              "take the bold chance when it feels right, and don't fear the unconventional path. That's where your fortune actually lives.")
    else:
        kind='balanced'
        text=("Here's something about how your life works: <b>you've got a genuine blend of earned reward and lucky timing.</b> "
              "Some of your wins come through patient effort and preparation, and some arrive through unexpected openings and good timing. "
              "This is actually a flexible, resilient way to be wired — when the slow road is blocked, a sudden door tends to open, and "
              "vice versa. Pay attention to which mode a given goal calls for: some things reward grinding it out, and others reward "
              "taking the leap. Your real skill is knowing which is which.")

    return {'merit':merit,'luck':luck,'kind':kind,'text':text}

if __name__=='__main__':
    import engine, strength as st_mod
    c=engine.compute_chart(1995,12,6,22,0,26.6483,85.80,5.75)
    st=st_mod.planet_strength(c)
    sig=reward_signature(c, st)
    print(f"Merit score: {sig['merit']} | Luck score: {sig['luck']} | Type: {sig['kind']}")
    print()
    print(sig['text'].replace('<b>','').replace('</b>',''))
