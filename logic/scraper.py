import os
import requests
from datetime import datetime, timedelta

CARRIER_METRICS = {
    "DL": {"name": "Delta",     "comfort": 85, "baggage_fee": "$30", "on_time": 83},
    "NK": {"name": "Spirit",    "comfort": 30, "baggage_fee": "$79", "on_time": 71},
    "UA": {"name": "United",    "comfort": 75, "baggage_fee": "$35", "on_time": 79},
    "B6": {"name": "JetBlue",   "comfort": 90, "baggage_fee": "$0",  "on_time": 76},
    "AA": {"name": "American",  "comfort": 78, "baggage_fee": "$30", "on_time": 78},
    "WN": {"name": "Southwest", "comfort": 72, "baggage_fee": "$0",  "on_time": 80},
    "F9": {"name": "Frontier",  "comfort": 40, "baggage_fee": "$49", "on_time": 72},
    "AS": {"name": "Alaska",    "comfort": 82, "baggage_fee": "$30", "on_time": 85},
}

SERPAPI_URL       = "https://serpapi.com/search"
AVIATIONSTACK_URL = "http://api.aviationstack.com/v1/flights"


class FlightScraper:
    def __init__(self):
        self.serpapi_key = os.getenv("SERPAPI_KEY", "")
        self.av_key      = os.getenv("AVIATIONSTACK_KEY", "")

    # ------------------------------------------------------------------
    # Main entry point — SerpAPI first, AviationStack as fallback
    # ------------------------------------------------------------------
    def fetch_live_flights(self, origin, dest, date=None):
        flights = self._fetch_serpapi(origin, dest, date)
        if not flights:
            flights = self._fetch_aviationstack(origin, dest)
        return flights  # None triggers DEFAULT_FLIGHTS fallback in app.py

    # ------------------------------------------------------------------
    # SerpAPI (Google Flights) — real prices, duration, stops, times
    # ------------------------------------------------------------------
    def _fetch_serpapi(self, origin, dest, date=None):
        if not self.serpapi_key or self.serpapi_key == "YOUR_SERPAPI_KEY":
            return None
        if not date:
            date = (datetime.today() + timedelta(days=30)).strftime("%Y-%m-%d")
        try:
            resp = requests.get(SERPAPI_URL, params={
                "engine":         "google_flights",
                "departure_id":   origin,
                "arrival_id":     dest,
                "outbound_date":  date,
                "currency":       "USD",
                "hl":             "en",
                "type":           2,
                "api_key":        self.serpapi_key,
            }, timeout=15)
            resp.raise_for_status()
            data    = resp.json()
            print(f"[SerpAPI] status={resp.status_code} keys={list(data.keys())}")
            print(f"[SerpAPI] best_flights={len(data.get('best_flights', []))} other_flights={len(data.get('other_flights', []))}")
            if "error" in data:
                print(f"[SerpAPI] error: {data['error']}")
            flights = data.get("best_flights", []) + data.get("other_flights", [])
            if not flights:
                return None
            return [r for r in (self._parse_serpapi_flight(f) for f in flights) if r]
        except Exception as e:
            print(f"SerpAPI error: {e}")
            try:
                print(f"SerpAPI response body: {resp.json()}")
            except Exception:
                pass
            return None

    def _parse_serpapi_flight(self, f):
        segments = f.get("flights", [])
        if not segments:
            return None

        first = segments[0]
        last  = segments[-1]

        airline_name   = first.get("airline", "Unknown")
        total_duration = f.get("total_duration", 300)  # already in minutes
        stops          = len(segments) - 1
        price          = f.get("price")

        code = next((k for k, v in CARRIER_METRICS.items()
                     if v["name"].lower() in airline_name.lower()), None)
        m    = CARRIER_METRICS.get(code, {"comfort": 70, "baggage_fee": "Varies", "on_time": 75})

        h, mins      = divmod(total_duration, 60)
        duration_str = f"{h}h {mins:02d}m" if h else f"{mins}m"

        dep_time = first.get("departure_airport", {}).get("time", "N/A")
        arr_time = last.get("arrival_airport",   {}).get("time", "N/A")
        # SerpAPI time format: "2024-01-15 08:30" — keep only HH:MM
        dep_time = dep_time[-5:] if len(dep_time) > 5 else dep_time
        arr_time = arr_time[-5:] if len(arr_time) > 5 else arr_time

        return {
            "airline":       airline_name,
            "logo":          "✈️",
            "price":         float(price) if price else None,
            "route":         "Nonstop" if stops == 0 else f"{stops} Stop{'s' if stops > 1 else ''}",
            "stops":         stops,
            "duration":      duration_str,
            "duration_mins": total_duration,
            "departure":     dep_time,
            "arrival":       arr_time,
            "comfort_score": m.get("comfort", 70),
            "baggage":       m.get("baggage_fee", "Varies"),
            "baggage_score": 100 if m.get("baggage_fee") == "$0" else 60,
            "on_time":       m.get("on_time", 75),
            "service_score": 75,
            "timing_score":  80,
        }

    # ------------------------------------------------------------------
    # AviationStack — real departure/arrival times, fallback when no
    # SerpAPI key is set
    # ------------------------------------------------------------------
    def _fetch_aviationstack(self, origin, dest):
        if not self.av_key:
            return None
        try:
            resp = requests.get(AVIATIONSTACK_URL, params={
                "access_key": self.av_key,
                "dep_iata":   origin,
                "arr_iata":   dest,
                "limit":      10,
            }, timeout=10)
            resp.raise_for_status()
            data = resp.json().get("data", [])
            if not data:
                return None
            return [self._parse_av_flight(f) for f in data
                    if f.get("flight_status") != "cancelled"]
        except Exception as e:
            print(f"AviationStack error: {e}")
            return None

    def _parse_av_flight(self, f):
        airline_name = f.get("airline", {}).get("name", "Unknown")
        iata_code    = f.get("airline", {}).get("iata", "")
        dep          = f.get("departure", {})
        arr          = f.get("arrival",   {})

        dep_time = (dep.get("estimated") or dep.get("scheduled") or "")
        arr_time = (arr.get("estimated") or arr.get("scheduled") or "")
        dep_time = dep_time[11:16] if len(dep_time) > 10 else dep_time
        arr_time = arr_time[11:16] if len(arr_time) > 10 else arr_time

        m = CARRIER_METRICS.get(iata_code, {
            "name": airline_name, "comfort": 70, "baggage_fee": "Varies", "on_time": 75
        })

        return {
            "airline":       m.get("name", airline_name),
            "logo":          "✈️",
            "price":         None,
            "route":         "Nonstop",
            "stops":         0,
            "duration":      "N/A",
            "duration_mins": 300,
            "departure":     dep_time or "N/A",
            "arrival":       arr_time or "N/A",
            "comfort_score": m.get("comfort", 70),
            "baggage":       m.get("baggage_fee", "Varies"),
            "baggage_score": 100 if m.get("baggage_fee") == "$0" else 60,
            "on_time":       m.get("on_time", 75),
            "service_score": 75,
            "timing_score":  80,
        }

    # ------------------------------------------------------------------
    # Enrich fallback mock data
    # ------------------------------------------------------------------
    def enrich_results(self, flights):
        for f in flights:
            if "comfort_score" not in f:
                name = f.get("airline", "")
                code = next((k for k, v in CARRIER_METRICS.items() if v["name"] == name), None)
                m    = CARRIER_METRICS.get(code, {"comfort": 60, "baggage_fee": "Varies", "on_time": 75})
                f.update({
                    "comfort_score": m["comfort"],
                    "baggage":       m["baggage_fee"],
                    "baggage_score": 100 if m["baggage_fee"] == "$0" else 60,
                    "on_time":       m["on_time"],
                    "service_score": 75,
                    "timing_score":  80,
                    "duration":      "N/A",
                    "duration_mins": 300,
                    "departure":     "N/A",
                    "arrival":       "N/A",
                    "stops":         0 if f.get("route") == "Nonstop" else 1,
                })
        return flights
