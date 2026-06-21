"""
Antardasha — Five-Year Vedic Forecast
A small Flask server. The user enters only date, time, and place;
coordinates and the historically-correct timezone are computed internally.

Run:
    pip install -r requirements.txt
    python app.py
    open http://localhost:8000
"""
from flask import Flask, request, jsonify, send_from_directory
import engine, interpret, places
import os

app = Flask(__name__, static_folder='.')

@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

@app.route('/api/countries')
def countries():
    return jsonify(places.list_countries())

@app.route('/api/cities')
def cities():
    cc = request.args.get('cc', '')
    return jsonify(places.cities_in(cc))

@app.route('/api/places')
def place_search():
    q = request.args.get('q', '')
    return jsonify(places.search_places(q))

@app.route('/api/daily', methods=['POST'])
def daily():
    d = request.get_json()
    try:
        import daily as daily_mod
        chart = engine.compute_from_place(
            int(d['year']), int(d['month']), int(d['day']),
            int(d['hour']), int(d['minute']),
            float(d['lat']), float(d['lon']))
        moon = chart['planets']['Moon']['lon']
        asc = chart['ascendant']['lon']
        md = chart['current_mahadasha']
        r = daily_mod.daily_reading(moon, asc, md)
        lines = daily_mod.daily_text(r)
        return jsonify({'stars': r['stars'], 'lines': lines, 'date': r['date'],
                        'love': r['love_stars'], 'money': r['money_stars'],
                        'work': r['work_stars'], 'mood': r['mood_stars'],
                        'ascendant': chart['ascendant']['sign'], 'moon_sign': chart['planets']['Moon']['sign']})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/monthly', methods=['POST'])
def monthly():
    d = request.get_json()
    try:
        import daily as daily_mod
        chart = engine.compute_from_place(
            int(d['year']), int(d['month']), int(d['day']),
            int(d['hour']), int(d['minute']),
            float(d['lat']), float(d['lon']))
        moon = chart['planets']['Moon']['lon']
        asc = chart['ascendant']['lon']
        md = chart['current_mahadasha']
        mr = daily_mod.monthly_reading(moon, asc, md)
        text = daily_mod.monthly_text(mr, md)
        return jsonify({'avg_stars': mr['avg_stars'], 'text': text,
                        'love': mr['love_stars'], 'money': mr['money_stars'], 'work': mr['work_stars'],
                        'best_days': mr['best_days'], 'hard_days': mr['hard_days'],
                        'month': mr['month'], 'year': mr['year']})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/overview', methods=['POST'])
def overview():
    d = request.get_json()
    try:
        import overview as ov, strength as st_mod, synthesis as syn_mod, exceptions as exc_mod, context as ctx_mod
        chart = engine.compute_from_place(
            int(d['year']), int(d['month']), int(d['day']),
            int(d['hour']), int(d['minute']),
            float(d['lat']), float(d['lon']))
        st = st_mod.planet_strength(chart)
        syn = syn_mod.full_synthesis(chart, st)
        excs = exc_mod.check_exceptions(chart, st)
        syn = exc_mod.apply_exceptions(syn, excs)
        life_ctx = ctx_mod.derive_context(chart)
        text = ov.current_chapter(chart, st, syn, life_ctx)
        return jsonify({'text': text})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/forecast', methods=['POST'])
def forecast():
    d = request.get_json()
    try:
        chart = engine.compute_from_place(
            int(d['year']), int(d['month']), int(d['day']),
            int(d['hour']), int(d['minute']),
            float(d['lat']), float(d['lon'])
        )
        sections = interpret.interpret(chart)
        for pl in chart['planets'].values():
            pl.pop('lon', None)
        chart['ascendant'].pop('lon', None)
        return jsonify({'chart': chart, 'sections': sections})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    print(f"\n  Antardasha running -> http://localhost:{port}\n")
    app.run(host='0.0.0.0', port=port, debug=False)
