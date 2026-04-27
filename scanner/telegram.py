import requests
import pandas as pd


def send_telegram_message(bot_token: str, chat_id: str, message: str) -> None:
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }

    response = requests.post(url, json=payload, timeout=30)
    response.raise_for_status()


def _safe_float(value, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return default


def _emoji_for_side(side: str) -> str:
    return "🟢" if str(side).upper() == "LONG" else "🔴"


def _stage_label(stage: str) -> str:
    stage_map = {
        "prep": "Pre-Market Prep",
        "live": "Live Scan",
        "range15": "15-Min Breakout Scan",
    }
    return stage_map.get(stage, stage.title())


def _confidence_label(score: float) -> str:
    if score >= 8:
        return "High"
    if score >= 6:
        return "Medium"
    return "Low"


def _risk_percent(entry: float, stop: float) -> float:
    if entry <= 0:
        return 0.0
    return abs(entry - stop) / entry * 100


def _clean_reason(reason: str) -> str:
    reason = str(reason).strip()
    if not reason:
        return "Conditions matched"
    return reason


def _format_signal_block(row: pd.Series, rank: int) -> str:
    symbol = str(row.get("symbol", "NA"))
    side = str(row.get("signal_side", "NA")).upper()
    entry = _safe_float(row.get("entry_price", 0))
    stop = _safe_float(row.get("stop_loss", 0))
    target = _safe_float(row.get("target_price", 0))
    rr_ratio = str(row.get("rr_ratio", "NA"))
    strategy = str(row.get("strategy_name", "NA"))
    reason = _clean_reason(row.get("reason", ""))
    score = _safe_float(row.get("score", 0))
    confidence = _confidence_label(score)
    risk_pct = _risk_percent(entry, stop)

    emoji = _emoji_for_side(side)

    return (
        f"<b>{rank}. {emoji} {symbol}</b>\n"
        f"📌 <b>Strategy:</b> {strategy}\n"
        f"↕️ <b>Side:</b> {side}\n"
        f"🎯 <b>Entry:</b> {entry:.2f}\n"
        f"🛑 <b>SL:</b> {stop:.2f}\n"
        f"💰 <b>Target:</b> {target:.2f}\n"
        f"⚖️ <b>R:R:</b> {rr_ratio}\n"
        f"📉 <b>Risk %:</b> {risk_pct:.2f}%\n"
        f"⭐ <b>Score:</b> {score:.2f} ({confidence})\n"
        f"📝 <b>Reason:</b> {reason}"
    )


def _format_section(df: pd.DataFrame, title: str, top_n: int) -> list[str]:
    lines = [f"<b>{title}</b>", ""]
    if df.empty:
        lines.append("No signals")
        lines.append("")
        return lines

    top_df = df.head(top_n)
    for idx, (_, row) in enumerate(top_df.iterrows(), start=1):
        lines.append(_format_signal_block(row, idx))
        lines.append("")

    return lines


def format_top_signals(
    df: pd.DataFrame,
    market: str | None = None,
    stage: str | None = None,
    top_n: int = 3,
) -> str:
    if df is None or df.empty:
        header = "📭 <b>No high-probability signals found.</b>"
        if market or stage:
            meta = []
            if market:
                meta.append(f"📈 <b>Market:</b> {market}")
            if stage:
                meta.append(f"⏱ <b>Stage:</b> {_stage_label(stage)}")
            return header + "\n" + "\n".join(meta)
        return header

    work_df = df.copy()

    if "score" in work_df.columns:
        work_df = work_df.sort_values(by="score", ascending=False)

    inferred_market = market or str(work_df.iloc[0].get("market", "NA"))
    inferred_stage = stage or str(work_df.iloc[0].get("stage", "NA"))
    scan_time = str(work_df.iloc[0].get("scan_time", ""))

    long_df = work_df[work_df["signal_side"].astype(str).str.upper() == "LONG"].copy()
    short_df = work_df[work_df["signal_side"].astype(str).str.upper() == "SHORT"].copy()

    lines = [
        "🚀 <b>Algo Trading Scanner Alert</b>",
        f"📈 <b>Market:</b> {inferred_market}",
        f"⏱ <b>Stage:</b> {_stage_label(inferred_stage)}",
    ]

    if scan_time:
        lines.append(f"🕒 <b>Scan Time:</b> {scan_time}")

    lines.append(f"📦 <b>Total Filtered Signals:</b> {len(work_df)}")
    lines.append("")

    lines.extend(_format_section(long_df, "🏆 Top Long Setups", top_n))
    lines.extend(_format_section(short_df, "🏆 Top Short Setups", top_n))

    lines.append("<b>Summary</b>")
    lines.append(f"🟢 Long Signals: {len(long_df)}")
    lines.append(f"🔴 Short Signals: {len(short_df)}")
    lines.append("")
    lines.append("⚠️ <i>For watchlist review only. Validate on chart before entry.</i>")

    return "\n".join(lines)
