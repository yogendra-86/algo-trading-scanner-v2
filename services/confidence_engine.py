class ConfidenceEngine:

    def calculate(self, score):
        if score >= 12:
            return "🔥 High"
        elif score >= 8:
            return "⚡ Medium"
        else:
            return "⚠️ Low"
