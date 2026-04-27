class SkyScoreEngine:
    def rank(self, flights, weights):
        if not flights:
            return []

        durations = [f.get("duration_mins", 300) for f in flights]
        min_dur, max_dur = min(durations), max(durations)

        for f in flights:
            p_score = max(0, 100 - ((f.get("price") or 500) / 10))

            dur = f.get("duration_mins", 300)
            t_score = 100 if max_dur == min_dur else 100 - ((dur - min_dur) / (max_dur - min_dur)) * 50

            d_score = 100 if f.get("route") == "Nonstop" else 50
            b_score = f.get("baggage_score", 70)
            c_score = f.get("comfort_score", 75)
            s_score = f.get("service_score", 85)

            f["sky_score"] = round(
                (p_score * weights["price"]) +
                (t_score * weights["timing"]) +
                (d_score * weights["direct"]) +
                (b_score * weights["baggage"]) +
                (c_score * weights["comfort"]) +
                (s_score * weights["service"]),
                1,
            )

        return sorted(flights, key=lambda x: x["sky_score"], reverse=True)
