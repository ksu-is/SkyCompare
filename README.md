# ✈ SkyCompare
SkyCompare is a web-based flight comparison tool built with Python and Flask. Instead of just showing the cheapest option, SkyCompare lets you rank what matters most to you and scores every flight accordingly.

---

## What It Does
Enter where you're flying from and to, pick a date, and choose your top 3 priorities. SkyCompare pulls live flight data, calculates a **SkyScore** for each result based on your preferences, and ranks them from best to worst.

---

## Features

**Smart Airport Search**
Type a city name or IATA code in the From/To fields and a filtered dropdown appears instantly. Supports 80+ US airports — select with mouse, arrow keys, or Enter.

**3-Priority Ranking System**
Choose your top 3 priorities from six factors. Your #1 pick carries the most weight (50%), followed by #2 (30%) and #3 (20%). Factors:
- Price
- Flight Duration
- Direct Routes
- Baggage Policy
- Seat Comfort
- Customer Service

**Live Flight Data**
- **SerpAPI (Google Flights)** — real prices, durations, stop counts, and departure/arrival times
- **AviationStack** — live schedule data as a fallback when no SerpAPI key is set
- Built-in demo data if neither API key is configured

**SkyScore Algorithm**
Each flight is scored across all six factors and weighted by your priority selections. Flights are sorted highest to lowest — the best match for *your* preferences is always #1.

**Direct Booking Links**
Every result includes a Book button linking to the airline's website. Southwest, American, United, and JetBlue links are pre-filled with your route and date. Other airlines link to their homepage.

**Red & Black UI**
Clean dark theme built on Bootstrap 5 with red accents. Top-ranked flight is highlighted. Priority pills show what you ranked at the top of results.

---

## Setup

1. Clone the repo and install dependencies:
```
pip install flask requests python-dotenv
```

2. Create a `.env` file in the project root:
```
SERPAPI_KEY=your_key_here
AVIATIONSTACK_KEY=your_key_here
```

3. Run the app:
```
python app.py
```

4. Open `http://localhost:9999` in your browser.

> API keys are optional — the app runs on demo data without them.

---

## Project Roadmap

### Completed
- [x] Flask app with route search and results page
- [x] SkyScore ranking engine with weighted factors
- [x] Per-airline comfort, baggage, and on-time metrics
- [x] AviationStack API integration (live schedules)
- [x] SerpAPI / Google Flights integration (real prices + duration)
- [x] Red and black dark theme with Bootstrap 5
- [x] Airport autocomplete dropdown (city name or IATA code)
- [x] 3-priority ranking system replacing sliders
- [x] Booking links with deep-link support for major airlines
- [x] Info box explaining booking link behavior

### Possible Next Steps
- [ ] Round-trip search support
- [ ] Filter results by nonstop only or max price
- [ ] More airlines and international airports
- [ ] Mobile layout improvements
- [ ] Save or share a search result
