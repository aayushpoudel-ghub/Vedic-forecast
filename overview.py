"""'Your current chapter' — a direct, jargon-free life overview.
Uses the dasha period nature + convergence verdicts + strongest/weakest planet
to tell the person, in plain words, how their time is running and what's ahead.
NO planet names, NO houses, NO dates. Just meaningful, personal, direct."""

# How each mahadasha period FEELS, in plain life terms (no planet names)
PERIOD_FEEL={
 'Sun':"a chapter about stepping into your own authority and being seen. Life is pushing you to stand up, be recognised, and take charge of your direction. It can feel intense — like you're being tested on who you really are — but it's building your confidence and standing.",
 'Moon':"a gentler, more emotional chapter. Your inner life, your home, and the people closest to you matter more than usual right now. It's a time for nurturing what you care about and listening to how you feel, rather than pushing hard.",
 'Mars':"a chapter full of drive and energy. You have the push to fight for what you want, tackle hard challenges, and get things done. The caution is to not let frustration or haste get the better of you — your energy is a tool, not a master.",
 'Mercury':"a busy, mentally active chapter. Your mind is sharp, ideas are flowing, and communication, learning, and quick thinking are your strengths now. Many things are moving at once — the skill is staying organised and focused.",
 'Jupiter':"one of the most fortunate chapters of your life. Things are expanding — opportunities, wisdom, recognition, and growth are all favoured. Doors that were closed start to open. This is a time to think bigger, learn, and reach for what you want, because the wind is genuinely at your back.",
 'Venus':"a pleasant, comfortable chapter. Life softens — relationships, beauty, enjoyment, and material ease come more naturally now. It's one of the smoother stretches, good for love and the finer things, as long as you don't drift into pure indulgence.",
 'Saturn':"a serious, hard-working chapter. Nothing comes quickly or for free right now — but what you build in this time is solid and lasting. It can feel heavy or slow, like a long climb, but it's quietly making you stronger, more disciplined, and more capable than before.",
 'Rahu':"an ambitious, restless chapter. You're being pulled toward big, unconventional things — new directions, bold moves, sometimes foreign or unfamiliar territory. It can bring sudden rises and dramatic change. The key is to stay grounded and not chase illusions.",
 'Ketu':"an inward, searching chapter. The outer world feels less satisfying, and something deeper is pulling at you — meaning, understanding, letting go of what no longer fits. It can feel uncertain or detached at times, but it's a profound period of growth and self-knowledge.",
}

def current_chapter(chart, pstrength, convergence, life_ctx=None):
    """Build the plain-language overview paragraph, life-stage aware."""
    md=chart['current_mahadasha']
    parts=[]

    # 0. life-stage frame (if known)
    if life_ctx and life_ctx.get('stage'):
        stage=life_ctx['stage']
        if stage in ('youth','early-adult'):
            parts.append("At this early, formative stage of your life,")
        elif stage=='building':
            parts.append("At this dynamic, decisive stage of your life,")
        elif stage=='established':
            parts.append("At this established stage of your life,")
        else:
            parts.append("At this mature stage of your life,")
        # lowercase the period feel to flow after the frame
        feel=PERIOD_FEEL.get(md,'a significant chapter of change and growth.')
        parts.append(f"you're moving through {feel}")
    else:
        parts.append(f"Right now, you're moving through {PERIOD_FEEL.get(md,'a significant chapter of change and growth.')}")

    # 2. the overall tone — are things broadly favourable or testing? (from convergence)
    if convergence:
        scores=[a['score'] for a in convergence.values()]
        avg=sum(scores)/len(scores)
        strong_areas=[k for k,a in convergence.items() if a['verdict'] in ('very strong','strong')]
        weak_areas=[k for k,a in convergence.items() if a['verdict'] in ('challenged','difficult')]
        plain={'career':'your work and ambitions','wealth':'your finances','marriage':'your relationships',
               'health':'your wellbeing','education':'your learning and growth'}
        if avg>0.6:
            parts.append("Overall, this is a genuinely promising time for you. More is working in your favour than against you, and if you put in the effort, the results are there to be had.")
        elif avg<-0.4:
            parts.append("Overall, this is a demanding stretch that's asking a lot of you. Things may feel like harder work than they should — but these periods pass, and they tend to leave you stronger and wiser than before.")
        else:
            parts.append("Overall, this is a mixed but workable time — some parts of life are flowing well while others ask for patience. A lot depends on where you put your energy.")
        # 3. where it's strong and where to take care
        if strong_areas:
            sa=' and '.join(plain[a] for a in strong_areas[:2])
            parts.append(f"Your real strength right now lies in {sa} — this is where life is most on your side, so lean into it.")
        if weak_areas:
            wa=' and '.join(plain[a] for a in weak_areas[:2])
            parts.append(f"The area that needs the most care is {wa} — not a disaster, but somewhere to move thoughtfully and not force things.")

    # 4. forward-looking, no dates, builds anticipation
    if md=='Jupiter':
        parts.append("The bigger picture ahead is bright: you're entering one of the most expansive and rewarding stretches of your life, and the next few years carry real opportunity for growth and success — if you reach for it.")
    elif md in ('Saturn','Ketu','Rahu'):
        parts.append("The road ahead asks for patience, but it's leading somewhere meaningful. The challenges of this period are shaping something lasting, and there's genuine light and reward waiting on the other side of the effort.")
    else:
        parts.append("The years ahead hold real movement and possibility for you — turning points that will shape the direction of your life, with both opportunities to seize and moments that will ask for care.")

    parts.append("Your full five-year forecast maps exactly when these openings and turning points arrive, month by month — so you know not just what's coming, but when to act.")

    return " ".join(parts)

if __name__=='__main__':
    import engine, strength, synthesis
    c=engine.compute_chart(1995,12,6,22,0,26.6483,85.80,5.75)
    st=strength.planet_strength(c)
    syn=synthesis.full_synthesis(c, st)
    print(current_chapter(c, st, syn))
