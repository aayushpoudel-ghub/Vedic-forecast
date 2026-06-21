# Antardasha — Five-Year Vedic Forecast

A web app that computes a real sidereal Vedic astrology chart from a birth date,
time, and place, and turns it into a five-year forecast covering career, wealth,
relationships, health, and remedies.

The astronomy is **real** — it uses the Swiss Ephemeris (the same library
professional jyotiṣa software uses) with the Lahiri ayanāṁśa. The engine has been
verified to reproduce known charts exactly (correct ascendant, planetary signs,
dignities, and Vimśottarī daśā dates).

---

## What's in the box

| File | What it does |
|------|--------------|
| `index.html` | The full front-end — hero, method, the cast form (date, time, place with autocomplete), and the result panel. Self-contained. |
| `engine.py` | The astronomical core. Computes sidereal longitudes, ascendant, house placements, dignities, navāṁśa basis, and the Vimśottarī daśā / antardaśā. |
| `places.py` | Offline place lookup — turns a city name into coordinates **and** the historically-correct timezone offset. No internet, no API keys. |
| `interpret.py` | The interpretation layer — turns the computed chart facts into forecast prose using a transparent rule engine. |
| `app.py` | A small Flask server that serves the page and exposes `/api/places` and `/api/forecast`. |

The user enters only **three things — date, time, and place.** They type their birth
city, pick it from a dropdown (each option shows its country, so there's no
ambiguity between e.g. London UK and London Canada), and the app works out the
latitude, longitude, and the correct timezone-with-historical-DST internally.

---

## Run it locally

```bash
pip install flask pyswisseph
python app.py
# open http://localhost:8000
```

Enter a birth date, time, place, the UTC offset **in effect on that date** at that
place, and latitude/longitude. The form returns the computed chart and forecast.

---

## Two important accuracy notes

1. **Timezone history is handled for you.** The single biggest source of wrong
   charts is using today's UTC offset for a historical birth. This app avoids that:
   `places.py` derives the timezone from the birth coordinates and applies the DST
   rules *in effect on the birth date* (via `timezonefinder` + `pytz`). It correctly
   returns, for example, +00:00 for a 2002 Morocco birth (no DST then) but +01:00
   for a 2010 one. The offline city database (`geonamescache`) covers 30,000+ cities.

2. **Birth time matters.** The ascendant moves ~1° every 4 minutes, so a rounded
   birth time makes the house-based predictions softer. The UI says so honestly.

---

## Making the readings richer (optional)

`interpret.py` is a **rule engine**: transparent, free, and consistent, but
necessarily more formulaic than a human jyotiṣī. To get readings closer to a
careful hand-written analysis, send the computed `chart` JSON to an LLM and have it
write the prose. Sketch:

```python
# in app.py, after computing `chart`:
prompt = f"""You are an experienced Vedic astrologer. Here is a computed sidereal
chart (Lahiri). Write a specific, grounded five-year forecast for career and wealth.
Be honest that a favorable period is permission for effort, not a guarantee.
Chart: {json.dumps(chart)}"""
# call your LLM of choice, return its text in place of (or alongside) sections
```

Keep the computation in Python (it must be exact); use the model only for the
*language*, never for the math.

---

## Deploy

It's a static page plus a tiny Python API, so almost anything works:

- **Render / Railway / Fly.io** — point at `app.py` (`gunicorn app:app`), set the
  Python buildpack, done.
- **A VPS** — `pip install`, run behind nginx + gunicorn.
- **Vercel / Netlify** — host `index.html` as static and run the engine as a
  serverless function (port `engine.py` into the function).

---

## Please read: what this is and isn't

The positions and dates are computed exactly. The **interpretation is a symbolic,
interpretive tradition — not a validated predictive science.** Present it honestly:

- A favorable period is **permission, not delivery** — it describes conditions under
  which effort tends to pay off, never a guaranteed outcome.
- It is **not** a substitute for medical, legal, financial, or psychological advice.
- It works best as a mirror for reflection, not a basis for irreversible decisions.

The interface already states this in good faith. If you publish it for others,
please keep that framing — it's the difference between a thoughtful tool and one
that misleads people about their lives.
