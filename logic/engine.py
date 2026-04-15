class SkyScoreEngine:
    def rank(self, flights, weights):
        if not flights: return []

        for f in flights:
            # Normalized scores (0-100)
            p_score = 100 - (f.get('price', 500) / 10) 
            t_score = f.get('timing_score', 80)
            d_score = 100 if f.get('route') == "Nonstop" else 50
            b_score = f.get('baggage_score', 70)
            c_score = f.get('comfort_score', 75)
            s_score = f.get('service_score', 85)

            # Calculation using weights from the form
            f['sky_score'] = round(
                (p_score * weights['price']) +
                (t_score * weights['timing']) +
                (d_score * weights['direct']) +
                (b_score * weights['baggage']) +
                (c_score * weights['comfort']) +
                (s_score * weights['service']), 
            1)

        return sorted(flights, key=lambda x: x['sky_score'], reverse=True)