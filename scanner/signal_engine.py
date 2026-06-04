import logging
import os

import pandas as pd
import pytz
import yfinance as yf
from datetime import datetime

from strategies.entry.bullish.breakout import breakout_entry
from strategies.entry.bullish.pullback import pullback_entry
from strategies.entry.bullish.vwap_strength import vwap_strength

from strategies.entry.bearish.breakdown import breakdown_entry
from strategies.entry.bearish.pullback import pullback_sell
from strategies.entry.bearish.vwap_weakness import vwap_weakness

from strategies.txt_strategy_loader import TxtStrategyLoader
from strategies.txt_strategy_evaluator import TxtStrategyEvaluator

logger = logging.getLogger(__name__)


class SignalEngine:

    # ======================================
    # LOAD SYMBOLS
    # ======================================
    def load_symbols(self, market):

        file_map = {
            "NSE": "data/watchlists/nse_symbols.csv",
            "NASDAQ": "data/watchlists/nasdaq_symbols.csv"
        }

        file_path = file_map.get(market)

        df = pd.read_csv(file_path)

        symbols = df["symbol"].dropna().tolist()

        if market == "NSE":

            symbols = [
                s if s.endswith(".NS")
                else f"{s}.NS"
                for s in symbols
            ]

        logger.info(
            f"Loaded {len(symbols)} symbols for {market}"
        )

        return symbols

    # ======================================
    # FETCH DATA
    # ======================================
    def fetch_data(self, symbol, interval="5m"):

        try:

            df = yf.download(
                symbol,
                period="5d",
                interval=interval,
                progress=False
            )

            if df is None or df.empty:
                return None

            # ==================================
            # FIX MULTIINDEX
            # ==================================
            if isinstance(df.columns, pd.MultiIndex):

                df.columns = (
                    df.columns.get_level_values(0)
                )

            df = df.loc[
                :,
                ~df.columns.duplicated()
            ]

            # ==================================
            # VWAP
            # ==================================
            df["vwap"] = (
                (
                    df["Close"] * df["Volume"]
                ).cumsum()
                / df["Volume"].cumsum()
            )

            return df

        except Exception as e:

            logger.error(
                f"{symbol} data fetch error: {e}"
            )

            return None

    # ======================================
    # SAVE RESULTS
    # ======================================
    def save_results(
        self,
        result_df,
        market,
        stage
    ):

        ist = pytz.timezone("Asia/Kolkata")

        today = datetime.now(ist).strftime(
            "%Y-%m-%d"
        )

        output_dir = (
            f"output/{market}/{today}"
        )

        os.makedirs(output_dir, exist_ok=True)

        file_path = (
            f"{output_dir}/"
            f"{market}_{stage}_FINAL.csv"
        )

        result_df.to_csv(
            file_path,
            index=False
        )

        logger.info(
            f"Final report generated: {file_path}"
        )

    # ======================================
    # RUN ENGINE
    # ======================================
    def run(
        self,
        market,
        stage,
        txt_strategy=None
    ):

        symbols = self.load_symbols(market)

        results = []

        # ==================================
        # TXT STRATEGIES
        # ==================================
        txt_loader = TxtStrategyLoader()

        txt_evaluator = TxtStrategyEvaluator()

        txt_strategies = (
            txt_loader.load_strategies(
                txt_strategy
            )
        )

        logger.info(
            f"Loaded TXT strategies: "
            f"{len(txt_strategies)}"
        )

        for symbol in symbols:

            df_5m = self.fetch_data(symbol)

            if df_5m is None or df_5m.empty:
                continue

            latest_price = float(
                df_5m["Close"].iloc[-1]
            )

            candle_time = str(
                df_5m.index[-1]
            )

            # ==================================
            # DEFAULT STRATEGY MODE
            # ==================================
            if txt_strategy is None:

                bullish_strategies = [
                    (
                        "breakout_entry",
                        breakout_entry
                    ),
                    (
                        "pullback_entry",
                        pullback_entry
                    ),
                    (
                        "vwap_strength",
                        vwap_strength
                    ),
                ]

                bearish_strategies = [
                    (
                        "breakdown_entry",
                        breakdown_entry
                    ),
                    (
                        "pullback_sell",
                        pullback_sell
                    ),
                    (
                        "vwap_weakness",
                        vwap_weakness
                    ),
                ]

                # ==============================
                # BULLISH
                # ==============================
                for (
                    strategy_name,
                    strategy_func
                ) in bullish_strategies:

                    try:

                        score = strategy_func(
                            df_5m,
                            market
                        )

                        if score >= 2:

                            results.append({
                                "symbol": symbol,
                                "strategy": strategy_name,
                                "direction": "bullish",
                                "price": latest_price,
                                "score": score,
                                "candle_time": candle_time
                            })

                    except Exception as e:

                        logger.error(
                            f"{symbol} bullish "
                            f"strategy error: {e}"
                        )

                # ==============================
                # BEARISH
                # ==============================
                for (
                    strategy_name,
                    strategy_func
                ) in bearish_strategies:

                    try:

                        score = strategy_func(
                            df_5m,
                            market
                        )

                        if score >= 2:

                            results.append({
                                "symbol": symbol,
                                "strategy": strategy_name,
                                "direction": "bearish",
                                "price": latest_price,
                                "score": score,
                                "candle_time": candle_time
                            })

                    except Exception as e:

                        logger.error(
                            f"{symbol} bearish "
                            f"strategy error: {e}"
                        )
            # ==================================
            # TXT STRATEGY MODE
            # ==================================
            else:

                for txt_strat in txt_strategies:

                    try:

                        # ======================
                        # TIMEFRAME
                        # ======================
                        timeframe = txt_strat.get(
                            "TIMEFRAME",
                            "5m"
                        )

                        tf_df = self.fetch_data(
                            symbol,
                            interval=timeframe
                        )

                        if (
                            tf_df is None
                            or tf_df.empty
                        ):
                            continue

                        score = (
                            txt_evaluator.evaluate(
                                txt_strat,
                                tf_df
                            )
                        )

                        if score <= 0:
                            continue

                        direction = (
                            "bullish"
                            if txt_strat["TYPE"]
                            == "BULLISH"
                            else "bearish"
                        )

                        results.append({

                            "symbol": symbol,

                            "strategy":
                                txt_strat["NAME"],

                            "direction":
                                direction,

                            "price": float(
                                tf_df["Close"]
                                .iloc[-1]
                            ),

                            "score": score,

                            "timeframe":
                                timeframe,

                            "candle_time": str(
                                tf_df.index[-1]
                            )
                        })

                    except Exception as e:

                        logger.error(
                            f"TXT strategy "
                            f"error: {e}"
                        )

        if not results:

            logger.warning(
                "No signals generated"
            )
            return pd.DataFrame()

        result_df = pd.DataFrame(results)

        logger.info(
            f"Total signals: {len(result_df)}"
        )

        self.save_results(
            result_df,
            market,
            stage
        )

        return result_df
