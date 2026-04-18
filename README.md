# ✈ SkyCompare
SkyCompare is a web-based flight comparison tool built with Python and Flask. Instead of just showing the cheapest flight, SkyCompare lets users set their own priorities and ranks available flights based on what matters most to them — whether that's price, comfort, baggage policy, or getting there on time.

What It Does
When a user visits SkyCompare, they enter a departure airport and a destination airport using standard IATA codes (for example, ATL for Atlanta or LAX for Los Angeles). They then use a set of sliders to assign percentage weights to six different factors:

Price – How much the ticket costs
Timing – Whether the departure and arrival times are convenient
Direct Routes – Preference for nonstop flights over connecting ones
Baggage Policy – How generous the airline's baggage allowance is
Seat Comfort – Legroom, seat width, and overall comfort rating
Customer Service – The airline's reputation for passenger support

Once the user submits the form, SkyCompare pulls flight data (live via the AviationStack API, or from built-in mock data if no API key is set), enriches each result with airline quality metrics, and calculates a SkyScore for every flight. Flights are then ranked from highest to lowest SkyScore and displayed in a clean results table.

Features

Simple two-field route search (origin and destination)
Six customizable priority sliders
SkyScore ranking algorithm that weights each factor based on user input
Per-airline comfort, baggage, and service ratings built in
Live flight data via AviationStack API (optional — works without a key using demo data)
Clean, responsive UI using Bootstrap 5
Color-coded SkyScore badges (green for high scores, blue for others)
