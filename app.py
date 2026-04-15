import os
from flask import Flask, render_template, request
from logic.engine import SkyScoreEngine
from logic.scraper import FlightScraper

app = Flask(__name__)

# Mock data for when API is unavailable
DEFAULT_FLIGHTS = [
    {"airline": "Delta", "price": 450, "route": "Nonstop", "logo": "✈️"},
    {"airline": "Spirit", "price": 110, "route": "1 Stop", "logo": "✈️"},
    {"airline": "United", "price": 380, "route": "Nonstop", "logo": "✈️"},
    {"airline": "JetBlue", "price": 290, "route": "Nonstop", "logo": "✈️"}
]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    origin = request.form.get('origin', 'ATL').upper()
    dest = request.form.get('dest', 'LAX').upper()

    # Capture all 6 weights
    weights = {
        'price': int(request.form.get('weight_price', 0)) / 100,
        'timing': int(request.form.get('weight_timing', 0)) / 100,
        'direct': int(request.form.get('weight_direct', 0)) / 100,
        'baggage': int(request.form.get('weight_baggage', 0)) / 100,
        'comfort': int(request.form.get('weight_comfort', 0)) / 100,
        'service': int(request.form.get('weight_service', 0)) / 100
    }

    # API Logic
    scraper = FlightScraper()
    # If you get an API key, put it in scraper.py
    raw_flights = scraper.fetch_live_flights(origin, dest) or DEFAULT_FLIGHTS
    enriched_data = scraper.enrich_results(raw_flights)
    
    engine = SkyScoreEngine()
    ranked_results = engine.rank(enriched_data, weights)

    return render_template('results.html', flights=ranked_results, origin=origin, dest=dest)

if __name__ == '__main__':
    app.run(debug=True, port=9999)