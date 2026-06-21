"""User context layer — the information a master gathers by ASKING.
Focuses the reading on what the person actually wants, and filters out
predictions that don't apply to their life stage. Optional; defaults gracefully."""

def focus_reading(sections, ctx):
    """Reorder/annotate sections based on the person's stated focus & life facts.
    ctx keys (all optional): age, focus (list), married (bool), working (bool/str)."""
    if not ctx:
        return sections, None

    focus = ctx.get('focus', [])
    age = ctx.get('age')
    married = ctx.get('married')
    working = ctx.get('working')

    intro_bits=[]

    # life-stage framing
    if age:
        if age < 25:
            intro_bits.append("As someone early in life's journey, the emphasis falls naturally on education, finding direction, and laying foundations")
        elif age < 40:
            intro_bits.append("At this building stage of life, career growth, relationships, and establishing yourself are the live themes")
        elif age < 60:
            intro_bits.append("At this established stage, consolidation, leadership, wealth, and family take centre stage")
        else:
            intro_bits.append("At this mature stage, the focus turns to legacy, wellbeing, wisdom, and what endures")

    # marriage filter — don't predict marriage timing for the already-married
    note=None
    if married is True:
        note='married'
    elif married is False and age and age>25:
        intro_bits.append("with partnership a relevant and active theme")

    # working/studying
    if working == 'studying':
        intro_bits.append("Your studies and the path from them into work are a natural priority right now")
    elif working == 'working':
        intro_bits.append("Your career and its next steps are a natural priority right now")

    intro = '. '.join(intro_bits)+'.' if intro_bits else None

    # build a focused ordering: put requested areas first
    AREA_TO_SECTION={'career':'career','wealth':'wealth','love':'relationships',
                     'marriage':'relationships','health':'health','spiritual':'deeper',
                     'education':'career'}
    return sections, {'intro':intro, 'note':note, 'priority':[AREA_TO_SECTION.get(f) for f in focus if f in AREA_TO_SECTION]}

def adjust_marriage_section(text, married):
    """If already married, reframe the relationship section away from 'will you marry'."""
    if married is True:
        return ("In your marriage and partnership, "+text.split('. ',1)[-1] if '. ' in text else text).replace(
            'Partnership is read','Your existing partnership is read')
    return text

if __name__=='__main__':
    # demo
    ctx={'age':23,'focus':['career','wealth'],'married':False,'working':'studying'}
    _,meta=focus_reading({'career':'x','wealth':'y','relationships':'z'},ctx)
    print("Context intro:", meta['intro'])
    print("Priority sections:", meta['priority'])
    print("Marriage note:", meta['note'])
