"""Offline place lookup: place name -> coordinates + historical timezone offset.
Uses geonamescache (bundled city DB, no internet) + timezonefinder + pytz."""
import geonamescache
from timezonefinder import TimezoneFinder
import pytz
from datetime import datetime

_gc = geonamescache.GeonamesCache()
_cities = _gc.get_cities()
_countries = _gc.get_countries()
_tf = TimezoneFinder()

# Build a fast search list once
_CITY_LIST = []
for c in _cities.values():
    cc = c.get('countrycode', '')
    country = _countries.get(cc, {}).get('name', cc)
    _CITY_LIST.append({
        'name': c['name'],
        'country': country,
        'cc': cc,
        'lat': c['latitude'],
        'lon': c['longitude'],
        'pop': c.get('population', 0)
    })

def list_countries():
    """All countries that have at least one city, alphabetical."""
    seen = {}
    for c in _CITY_LIST:
        if c['cc'] and c['cc'] not in seen:
            seen[c['cc']] = c['country']
    return sorted([{'cc': k, 'name': v} for k, v in seen.items()], key=lambda x: x['name'])

def cities_in(cc):
    """All cities for a country code, largest first, with coordinates."""
    out = [c for c in _CITY_LIST if c['cc'] == cc]
    out.sort(key=lambda c: -c['pop'])
    return [{'label': c['name'], 'lat': c['lat'], 'lon': c['lon']} for c in out]

def search_places(query, limit=8):
    """Return matching cities for an autocomplete box, best/biggest first."""
    q = query.strip().lower()
    if len(q) < 2:
        return []
    starts = [c for c in _CITY_LIST if c['name'].lower().startswith(q)]
    contains = [c for c in _CITY_LIST if q in c['name'].lower() and not c['name'].lower().startswith(q)]
    starts.sort(key=lambda c: -c['pop'])
    contains.sort(key=lambda c: -c['pop'])
    out = (starts + contains)[:limit]
    return [{'label': f"{c['name']}, {c['country']}", 'lat': c['lat'], 'lon': c['lon']} for c in out]

def offset_for(lat, lon, year, month, day, hour, minute):
    """Return the historically-correct UTC offset (in hours) for a place & datetime."""
    tzname = _tf.timezone_at(lat=lat, lng=lon)
    if not tzname:
        tzname = _tf.closest_timezone_at(lat=lat, lng=lon) or 'UTC'
    tz = pytz.timezone(tzname)
    dt = tz.localize(datetime(year, month, day, hour, minute))
    off = dt.utcoffset()
    return off.total_seconds()/3600.0, tzname

if __name__ == '__main__':
    print(search_places('kathm'))
    print(search_places('marr'))
    print(offset_for(26.6483, 85.80, 1995, 12, 6, 22, 0))
    print(offset_for(31.63, -7.98, 2002, 6, 6, 23, 0))
