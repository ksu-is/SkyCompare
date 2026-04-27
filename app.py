import os
from flask import Flask, render_template, request
from dotenv import load_dotenv
from logic.engine import SkyScoreEngine
from logic.scraper import FlightScraper

load_dotenv()

app = Flask(__name__)

AIRPORTS = {
    "atlanta": "ATL", "hartsfield": "ATL",
    "los angeles": "LAX",
    "new york": "JFK", "john f kennedy": "JFK", "kennedy": "JFK",
    "newark": "EWR",
    "laguardia": "LGA", "la guardia": "LGA",
    "chicago": "ORD", "ohare": "ORD", "o'hare": "ORD",
    "midway": "MDW",
    "dallas": "DFW", "fort worth": "DFW", "dallas fort worth": "DFW",
    "dallas love": "DAL",
    "miami": "MIA",
    "orlando": "MCO",
    "san francisco": "SFO",
    "seattle": "SEA", "tacoma": "SEA", "seattle tacoma": "SEA",
    "denver": "DEN",
    "las vegas": "LAS",
    "boston": "BOS", "logan": "BOS",
    "washington": "DCA", "reagan": "DCA",
    "dulles": "IAD",
    "houston": "IAH", "intercontinental": "IAH",
    "hobby": "HOU",
    "phoenix": "PHX",
    "minneapolis": "MSP",
    "detroit": "DTW",
    "charlotte": "CLT",
    "philadelphia": "PHL",
    "salt lake city": "SLC",
    "portland": "PDX",
    "san diego": "SAN",
    "tampa": "TPA",
    "nashville": "BNA",
    "new orleans": "MSY",
    "memphis": "MEM",
    "kansas city": "MCI",
    "st louis": "STL", "saint louis": "STL",
    "baltimore": "BWI",
    "pittsburgh": "PIT",
    "cleveland": "CLE",
    "columbus": "CMH",
    "indianapolis": "IND",
    "cincinnati": "CVG",
    "raleigh": "RDU", "durham": "RDU",
    "austin": "AUS",
    "san antonio": "SAT",
    "sacramento": "SMF",
    "oakland": "OAK",
    "san jose": "SJC",
    "fort lauderdale": "FLL",
    "jacksonville": "JAX",
    "honolulu": "HNL",
    "anchorage": "ANC",
    "louisville": "SDF",
    "buffalo": "BUF",
    "milwaukee": "MKE",
    "boise": "BOI",
    "spokane": "GEG",
    "reno": "RNO",
    "albuquerque": "ABQ",
    "tucson": "TUS",
    "el paso": "ELP",
    "oklahoma city": "OKC",
    "tulsa": "TUL",
    "omaha": "OMA",
    "richmond": "RIC",
    "norfolk": "ORF",
    "greenville": "GSP",
    "charleston": "CHS",
    "savannah": "SAV",
    "knoxville": "TYS",
    "birmingham": "BHM",
    "little rock": "LIT",
    "baton rouge": "BTR",
    "jackson": "JAN",
    "burbank": "BUR",
    "long beach": "LGB",
    "ontario": "ONT",
    "palm springs": "PSP",
    "santa barbara": "SBA",
    "fresno": "FAT",
}

PRIORITY_LABELS = {
    'price':   'Price',
    'timing':  'Flight Duration',
    'direct':  'Direct Routes',
    'baggage': 'Baggage Policy',
    'comfort': 'Seat Comfort',
    'service': 'Customer Service',
}

def resolve_airport(value):
    value = value.strip()
    if len(value) == 3 and value.isalpha():
        return value.upper()
    return AIRPORTS.get(value.lower(), value.upper())

DEFAULT_FLIGHTS = [
    {"airline": "Delta",   "price": 450, "route": "Nonstop", "logo": "✈️"},
    {"airline": "Spirit",  "price": 110, "route": "1 Stop",  "logo": "✈️"},
    {"airline": "United",  "price": 380, "route": "Nonstop", "logo": "✈️"},
    {"airline": "JetBlue", "price": 290, "route": "Nonstop", "logo": "✈️"},
]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    origin = resolve_airport(request.form.get('origin', 'ATL'))
    dest   = resolve_airport(request.form.get('dest',   'LAX'))
    date   = request.form.get('date', '')

    p1 = request.form.get('priority_1', 'price')
    p2 = request.form.get('priority_2', 'timing')
    p3 = request.form.get('priority_3', 'direct')

    weights = {'price': 0, 'timing': 0, 'direct': 0, 'baggage': 0, 'comfort': 0, 'service': 0}
    weights[p1] = 0.50
    weights[p2] = 0.30
    weights[p3] = 0.20

    scraper     = FlightScraper()
    raw_flights = scraper.fetch_live_flights(origin, dest, date or None) or DEFAULT_FLIGHTS
    enriched    = scraper.enrich_results(raw_flights)

    engine  = SkyScoreEngine()
    results = engine.rank(enriched, weights)

    priorities = [PRIORITY_LABELS[p1], PRIORITY_LABELS[p2], PRIORITY_LABELS[p3]]

    return render_template('results.html', flights=results, origin=origin, dest=dest,
                           date=date, priorities=priorities)

if __name__ == '__main__':
    app.run(debug=True, port=9999)
