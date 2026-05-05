class ConfidenceEngine:
    def calculate(self, score):
        """
        Normalize score to percentage-based confidence
        """

        try:
            # Assume max score ~ 3 (based on your strategies)
            max_score = 3

            confidence = int((score / max_score) * 100)

            if confidence >= 70:
                return f"🔥 High ({confidence}%)"
            elif confidence >= 50:
                return f"⚡ Medium ({confidence}%)"
            else:
                return f"⚠️ Low ({confidence}%)"

        except Exception:
            return "⚠️ Low"
