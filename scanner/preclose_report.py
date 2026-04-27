from pathlib import Path
import pandas as pd
import yfinance as yf

from scanner.telegram import send_telegram_message


def _safe_float(value, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return default


def _ticker_for_market(symbol: str, market: str) -> str:
    symbol = str(symbol).strip().upper()

    if market == "NSE" and not symbol.endswith(".NS"):
        return f"{symbol}.NS"

    return symbol


def _normalize_download_df(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame()

    # Defensive flatten if a MultiIndex still appears
    if isinstance(df.columns, pd.MultiIndex):
        flattened = []
        for col in df.columns:
            if isinstance(col, tuple):
                # prefer the price field name, e.g. Close from ('Close', 'AAPL')
                flattened.append(str(col[0]))
            else:
                flattened.append(str(col))
        df.columns = flattened

    # normalize names for lookup
    df.columns = [str(c).strip().lower() for c in df.columns]
    return df


def _get_latest_intraday_price(symbol: str, market: str) -> float:
    ticker = _ticker_for_market(symbol, market)

    try:
        # intraday first
        df = yf.download(
            ticker,
            period="1d",
            interval="5m",
            auto_adjust=False,
            progress=False,
            threads=False,
            group_by="column",
            multi_level_index=False,
        )

        df = _normalize_download_df(df)

        if not df.empty and "close" in df.columns:
            series = df["close"].dropna()
            if not series.empty:
                return float(series.iloc[-1])

        print(f"⚠️ Intraday unavailable for {ticker}, trying daily fallback...")

        # fallback to latest daily close
        df_daily = yf.download(
            ticker,
            period="5d",
            interval="1d",
            auto_adjust=False,
            progress=False,
            threads=False,
            group_by="column",
            multi_level_index=False,
        )

        df_daily = _normalize_download_df(df_daily)

        if not df_daily.empty and "close" in df_daily.columns:
            series = df_daily["close"].dropna()
            if not series.empty:
                return float(series.iloc[-1])

        print(f"❌ No usable price for {ticker}")
        return 0.0

    except Exception as exc:
        print(f"❌ Error fetching {ticker}: {exc}")
        return 0.0


def _pnl_percent(side: str, entry: float, current_price: float) -> float:
    if entry <= 0 or current_price <= 0:
        return 0.0
    if str(side).upper() == "LONG":
        return ((current_price - entry) / entry) * 100
    return ((entry - current_price) / entry) * 100


def _status_from_pnl(pnl_pct: float) -> str:
    if pnl_pct > 0.3:
        return "In Profit"
    if pnl_pct < -0.3:
        return "In Loss"
    return "Near Entry"


def generate_preclose_report(tracker_path: Path, output_path: Path) -> Path | None:
    if not tracker_path.exists():
        return None

    df = pd.read_csv(tracker_path)
    if df.empty:
        return None

    rows = []
    for _, row in df.iterrows():
        symbol = str(row.get("symbol", "")).strip()
        market = str(row.get("market", "")).strip()
        side = str(row.get("signal_side", "")).strip().upper()
        entry = _safe_float(row.get("entry_price", 0))

        current_price = _get_latest_intraday_price(symbol, market)

        # skip broken rows instead of sending 0.00 alerts
        if current_price == 0.0:
            print(f"⚠️ Skipping {symbol} because current price could not be fetched")
            continue

        pnl_pct = _pnl_percent(side, entry, current_price)
        status = _status_from_pnl(pnl_pct)

        row_dict = row.to_dict()
        row_dict["current_price"] = round(current_price, 2)
        row_dict["pnl_pct"] = round(pnl_pct, 2)
        row_dict["status"] = status
        rows.append(row_dict)

    if not rows:
        return None

    out_df = pd.DataFrame(rows)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    out_df.to_csv(output_path, index=False)
    return output_path


def format_preclose_telegram_message(report_path: Path, market: str, run_date: str) -> str:
    df = pd.read_csv(report_path)
    if df.empty:
        return f"📭 <b>{market} Pre-Close Exit Alert</b>\nNo alerted symbols found."

    lines = [
        f"🔔 <b>{market} Pre-Close Exit Alert</b>",
        f"📅 <b>Date:</b> {run_date}",
        "",
    ]

    for idx, (_, row) in enumerate(df.iterrows(), start=1):
        symbol = row.get("symbol", "NA")
        side = str(row.get("signal_side", "NA")).upper()
        entry = _safe_float(row.get("entry_price", 0))
        current_price = _safe_float(row.get("current_price", 0))
        pnl_pct = _safe_float(row.get("pnl_pct", 0))
        strategy = row.get("strategy_name", "NA")
        status = row.get("status", "NA")

        emoji = "🟢" if side == "LONG" else "🔴"
        lines.extend([
            f"<b>{idx}. {emoji} {symbol} — {side}</b>",
            f"📌 <b>Strategy:</b> {strategy}",
            f"🎯 <b>Entry:</b> {entry:.2f}",
            f"🏁 <b>Current:</b> {current_price:.2f}",
            f"📊 <b>P&L:</b> {pnl_pct:.2f}%",
            f"🧭 <b>Status:</b> {status}",
            f"⛔ <b>Action:</b> Exit before market close",
            "",
        ])

    return "\n".join(lines)


def send_preclose_telegram(
    report_path: Path,
    market: str,
    run_date: str,
    bot_token: str,
    chat_id: str,
) -> None:
    message = format_preclose_telegram_message(report_path, market, run_date)
    send_telegram_message(bot_token, chat_id, message)
