from typing import Dict, List


class AlertFormatter:
    def format_current_trend(self, market: str, trend: str, session_label: str, as_of: str) -> str:
        return (
            f"📈 {market} Current Trend\n"
            f"As of: {as_of}\n"
            f"Session: {session_label}\n\n"
            f"Ideal trend to trade: {trend}"
        )

    def format_top5_alert(self, market: str, direction: str, picks: List[Dict], as_of: str) -> str:
        emoji = "🟢" if direction == "bullish" else "🔴"
        title = "Top 5 Bullish Stocks" if direction == "bullish" else "Top 5 Bearish Stocks"

        lines = [
            f"{emoji} {title} | {market}",
            f"As of: {as_of}",
            "",
        ]

        if not picks:
            lines.append("No qualified stocks shortlisted.")
            return "\n".join(lines)

        for idx, item in enumerate(picks[:5], start=1):
            lines.append(
                f"{idx}. {item.get('symbol', 'NA')} | "
                f"Strategy: {item.get('strategy', 'NA')} | "
                f"Score: {item.get('premium_score', 'NA')} | "
                f"RR: {item.get('rr', 'NA')} | "
                f"Confirmations: {item.get('confirmations', 1)} | "
                f"Entry: {item.get('entry', 'NA')} | "
                f"SL: {item.get('sl', 'NA')} | "
                f"Target: {item.get('target', 'NA')}"
            )

        return "\n".join(lines)

    def format_market_closed_eod(
        self,
        market: str,
        trend: str,
        bullish: List[Dict],
        bearish: List[Dict],
        as_of: str,
    ) -> str:
        lines = [
            f"📌 {market} Market is closed now",
            f"As of: {as_of}",
            "",
            f"📊 Today's Market Trend: {trend}",
            "",
            "🟢 Top 5 Bullish Performers:",
        ]

        if bullish:
            for idx, item in enumerate(bullish[:5], start=1):
                lines.append(
                    f"{idx}. {item.get('symbol', 'NA')} | "
                    f"Score: {item.get('premium_score', 'NA')} | "
                    f"RR: {item.get('rr', 'NA')} | "
                    f"Confirmations: {item.get('confirmations', 1)} | "
                    f"Strategy: {item.get('strategy', 'NA')}"
                )
        else:
            lines.append("No bullish performers found.")

        lines.extend(["", "🔴 Top 5 Bearish Performers:"])

        if bearish:
            for idx, item in enumerate(bearish[:5], start=1):
                lines.append(
                    f"{idx}. {item.get('symbol', 'NA')} | "
                    f"Score: {item.get('premium_score', 'NA')} | "
                    f"RR: {item.get('rr', 'NA')} | "
                    f"Confirmations: {item.get('confirmations', 1)} | "
                    f"Strategy: {item.get('strategy', 'NA')}"
                )
        else:
            lines.append("No bearish performers found.")

        return "\n".join(lines)
