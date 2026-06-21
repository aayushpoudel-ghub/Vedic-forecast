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
