"""User context — auto-derived from the birth date we already have.
Age-based life-stage tailoring (no need to ask), per the natural priorities
of each stage. Focuses the reading on what people at that stage actually care about."""

from datetime import datetime

def derive_context(chart):
    """From birth date alone, infer life-stage and the areas that naturally matter."""
    try:
        y,m,d = chart.get('_birth',(None,None,None))
    except Exception:
        y=None
    # birth year/month/day are passed in chart['_birth']; fall back gracefully
    by = chart.get('birth_year'); bm = chart.get('birth_month',1); bd = chart.get('birth_day',1)
    if not by:
        return None
    today = datetime.now()
    age = today.year - by - ((today.month, today.day) < (bm, bd))

    ctx = {'age': age}

    if age < 18:
        ctx['stage']='youth'
        ctx['focus']=['education','growth']
        ctx['frame']=("You're still early in life's journey, so the emphasis falls naturally on learning, "
            "finding your strengths, friendships, and discovering the direction that's right for you. "
            "The choices you make now about study and interests quietly shape the road ahead.")
        ctx['skip']=['marriage']
    elif age < 25:
        ctx['stage']='early-adult'
        ctx['focus']=['career','education','love']
        ctx['frame']=("You're at the threshold of adult life — stepping from study into the working world, "
            "figuring out your path, and beginning to think about independence, relationships, and what you want to build. "
            "It's a formative, fast-moving stage where the foundations are being laid.")
        ctx['skip']=[]
    elif age < 40:
        ctx['stage']='building'
        ctx['focus']=['career','wealth','love','marriage']
        ctx['frame']=("You're in the most dynamic stretch of life, where the big questions are live: how your career "
            "and finances will grow, the challenges and changes ahead at work, the major decisions that shape your path, "
            "and your love life and the question of partnership. This is the stage where the direction of your life takes shape.")
        ctx['skip']=[]
    elif age < 55:
        ctx['stage']='established'
        ctx['focus']=['career','wealth','health']
        ctx['frame']=("You're at an established stage of life, where the focus turns to consolidating what you've built — "
            "your career standing and finances, your family, your health, and the longer view of security and legacy. "
            "Stability and wise stewardship matter more now than chasing the new.")
        ctx['skip']=[]
    else:
        ctx['stage']='mature'
        ctx['focus']=['health','wealth','family']
        ctx['frame']=("You're at a mature and reflective stage of life, where wellbeing, family, peace of mind, "
            "and the legacy you leave take centre stage. It's a time to enjoy what you've built, tend to your health, "
            "and focus on what truly matters to you.")
        ctx['skip']=['marriage']

    return ctx

def stage_intro(ctx):
    """A plain-language opening line tailored to life stage."""
    if not ctx: return None
    return ctx.get('frame')

if __name__=='__main__':
    import engine
    c=engine.compute_chart(1995,12,6,22,0,26.6483,85.80,5.75)
    c['birth_year']=1995; c['birth_month']=12; c['birth_day']=6
    ctx=derive_context(c)
    print(f"Age: {ctx['age']} | Stage: {ctx['stage']}")
    print(f"Focus areas: {ctx['focus']}")
    print(f"Skip: {ctx['skip']}")
    print(f"\nFrame: {ctx['frame']}")

