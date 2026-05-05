import os
import time
import pandas as pd
import yfinance as yf
from datetime import datetime

from utils.logging_utils import get_logger

from strategies.common.indicators import add_indicators
from strategies.common.trend_filter import get_trend
from strategies.config.strategy_list import (
    BULLISH_STRATEGIES,
    BEARISH_STRATEGIES
)

logger = get_logger("signal_engine")


# ==============================
# FETCH DATA
# ==============================
def fetch_data(symbol, interval, retries=2):
    for attempt in range(retries):
        try:
            df = yf.download(
                symbol,
                period="10d",
                interval=interval,
                progress=False,
                threads=False
            )

            if df is None or df.empty:
                return None

            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            df = df.loc[:, ~df.columns.duplicated()]
            df = df.ffill()

            print(f"{symbol} ({interval}) → {df.index[-1]}")
            return df

        except Exception as e:
            print(f"Fetch error for {symbol}: {e}")

        time.sleep(1)

    return None


# ==============================
# PREPARE DATA
# ==============================
def prepare_df(df, min_candles=20):
    try:
        if df is None or df.empty:
            return None

        df = add_indicators(df)
        df.dropna(inplace=True)

        if len(df) < min_candles:
            return None

        return df

    except Exception as e:
        print(f"Indicator error: {e}")
        return None


# ==============================
# MAIN ENGINE
# ==============================
def run_stage_for_market(symbols, market, stage):

    results = []

    logger.info(f"Loaded {len(symbols)} symbols for {market}")

    for symbol in symbols:

        try:
            print("\n==============================")
            print(f"Processing: {symbol}")

            # ======================
            # FETCH DATA
            # ======================
            df_5m = fetch_data(symbol, "5m")
            df_15m = fetch_data(symbol, "15m")
            df_1h = fetch_data(symbol, "1h")

            if (
                df_5m is None or df_5m.empty or
                df_15m is None or df_15m.empty or
                df_1h is None or df_1h.empty
            ):
                print(f"{symbol} skipped due to missing data")
                continue

            # ======================
            # PREPARE DATA
            # ======================
            df_5m = prepare_df(df_5m, 50)
            df_15m = prepare_df(df_15m, 30)
            df_1h = prepare_df(df_1h, 15)

            if df_5m is None or df_15m is None or df_1h is None:
                print(f"{symbol} skipped due to insufficient data")
                continue

            # ======================
            # TREND DETECTION
            # ======================
            trend_15m = get_trend(df_15m)
            trend_1h = get_trend(df_1h)

            print(f"{symbol} → Trend15m: {trend_15m}, Trend1h: {trend_1h}")

            direction = trend_15m

            # ======================
            # STRATEGY SELECTION
            # ======================
            if direction == "bullish":
                strategies_to_run = BULLISH_STRATEGIES

            elif direction == "bearish":
                strategies_to_run = BEARISH_STRATEGIES

            else:
                # ✅ Neutral → run both
                print(f"{symbol} → Neutral trend → running BOTH strategies")
                strategies_to_run = BULLISH_STRATEGIES + BEARISH_STRATEGIES

            # ======================
            # EXECUTE STRATEGIES
            # ======================
            for strategy in strategies_to_run:
                try:
                    score = strategy(df_5m, market)

                    print(f"{symbol} - {strategy.__name__} → {score}")

                    if score >= 3:
                        direction_label = (
                            "bullish" if strategy in BULLISH_STRATEGIES else "bearish"
                        )

                        print(f"🔥 SIGNAL FOUND: {symbol} via {strategy.__name__}")

                        results.append({
                            "symbol": symbol,
                            "strategy": strategy.__name__,
                            "direction": direction_label,
                            "price": float(df_5m["Close"].iloc[-1]),
                            "score":score
                        })

                except Exception as e:
                    print(f"Strategy error {symbol}: {e}")

        except Exception as e:
            logger.warning(f"{symbol} processing failed: {e}")
            continue

    # ======================
    # SAVE OUTPUT
    # ======================
    if results:
        df_final = pd.DataFrame(results)

        today = datetime.now().strftime("%Y-%m-%d")
        output_dir = f"output/{market}/{today}"
        os.makedirs(output_dir, exist_ok=True)

        file_path = f"{output_dir}/{market}_{stage}_FINAL.csv"
        df_final.to_csv(file_path, index=False)

        logger.info(f"Final report generated: {file_path}")
        logger.info(f"Total signals: {len(df_final)}")

        return df_final

    else:
        logger.info("No signals generated")
        return pd.DataFrame()
