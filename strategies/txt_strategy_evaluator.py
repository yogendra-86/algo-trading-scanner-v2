import re

from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator


class TxtStrategyEvaluator:

    # ======================================
    # GET VALUE
    # ======================================
    def get_value(
        self,
        token,
        values
    ):

        token = token.strip()

        # ==================================
        # NUMBER
        # ==================================
        try:
            return float(token)

        except:
            pass

        # ==================================
        # VARIABLE
        # ==================================
        return values.get(token)

    # ======================================
    # EVALUATE SINGLE CONDITION
    # ======================================
    def evaluate_condition(
        self,
        condition,
        values
    ):

        pattern = (
            r"(.+?)\s*"
            r"(>|<|>=|<=|==)\s*"
            r"(.+)"
        )

        match = re.match(
            pattern,
            condition
        )

        if not match:
            return False

        left, operator, right = (
            match.groups()
        )

        left_value = self.get_value(
            left,
            values
        )

        right_value = self.get_value(
            right,
            values
        )

        if (
            left_value is None
            or right_value is None
        ):
            return False

        # ==================================
        # OPERATORS
        # ==================================
        if operator == ">":
            return left_value > right_value

        if operator == "<":
            return left_value < right_value

        if operator == ">=":
            return left_value >= right_value

        if operator == "<=":
            return left_value <= right_value

        if operator == "==":
            return left_value == right_value

        return False

    # ======================================
    # CROSSOVER CHECK
    # ======================================
    def evaluate_crossover(
        self,
        condition,
        values,
        previous_values
    ):

        if " crosses " not in condition:
            return False

        left, right = condition.split(
            " crosses "
        )

        left = left.strip()
        right = right.strip()

        current_left = values.get(left)
        current_right = values.get(right)

        previous_left = previous_values.get(left)
        previous_right = previous_values.get(right)

        if (
            current_left is None
            or current_right is None
            or previous_left is None
            or previous_right is None
        ):
            return False

        # ==================================
        # BULLISH CROSS
        # ==================================
        bullish_cross = (
            previous_left <= previous_right
            and current_left > current_right
        )

        # ==================================
        # BEARISH CROSS
        # ==================================
        bearish_cross = (
            previous_left >= previous_right
            and current_left < current_right
        )

        return bullish_cross or bearish_cross

    # ======================================
    # MAIN EVALUATION
    # ======================================
    def evaluate(
        self,
        strategy,
        df
    ):

        try:

            # ==================================
            # BASIC VALUES
            # ==================================
            close = float(
                df["Close"].iloc[-1]
            )

            open_price = float(
                df["Open"].iloc[-1]
            )

            high = float(
                df["High"].iloc[-1]
            )

            low = float(
                df["Low"].iloc[-1]
            )

            prev_high = float(
                df["High"].iloc[-2]
            )

            prev_low = float(
                df["Low"].iloc[-2]
            )

            sma20 = float(
                df["Close"]
                .rolling(20)
                .mean()
                .iloc[-1]
            )

            sma50 = float(
                df["Close"]
                .rolling(50)
                .mean()
                .iloc[-1]
            )

            volume = float(
                df["Volume"].iloc[-1]
            )

            avg_volume = float(
                df["Volume"]
                .rolling(20)
                .mean()
                .iloc[-1]
            )

            vwap = float(
                df["vwap"].iloc[-1]
            )

            # ==================================
            # EMA
            # ==================================
            ema20 = EMAIndicator(
                close=df["Close"],
                window=20
            ).ema_indicator().iloc[-1]

            ema50 = EMAIndicator(
                close=df["Close"],
                window=50
            ).ema_indicator().iloc[-1]

            # ==================================
            # RSI
            # ==================================
            rsi = RSIIndicator(
                close=df["Close"],
                window=14
            ).rsi().iloc[-1]

            # ==================================
            # VALUE MAP
            # ==================================
            values = {

                "close": close,
                "open": open_price,
                "high": high,
                "low": low,

                "prev_high": prev_high,
                "prev_low": prev_low,

                "sma20": sma20,
                "sma50": sma50,

                "ema20": ema20,
                "ema50": ema50,

                "vwap": vwap,

                "volume": volume,
                "avg_volume": avg_volume,

                "rsi": rsi,
            }

            # ==================================
            # PREVIOUS VALUES
            # ==================================
            previous_values = {

                "close": float(
                    df["Close"].iloc[-2]
                ),

                "vwap": float(
                    df["vwap"].iloc[-2]
                ),

                "ema20": EMAIndicator(
                    close=df["Close"],
                    window=20
                ).ema_indicator().iloc[-2],

                "ema50": EMAIndicator(
                    close=df["Close"],
                    window=50
                ).ema_indicator().iloc[-2],

                "rsi": RSIIndicator(
                    close=df["Close"],
                    window=14
                ).rsi().iloc[-2],
            }

            # ==================================
            # EVALUATE CONDITIONS
            # ==================================
            for condition in strategy[
                "conditions"
            ]:
                # ==============================
                # CROSSOVER
                # ==============================
                if " crosses " in condition:

                    result = (
                        self.evaluate_crossover(
                            condition,
                            values,
                            previous_values
                        )
                    )

                # ==============================
                # AND LOGIC
                # ==============================
                if " AND " in condition:

                    parts = condition.split(
                        " AND "
                    )

                    result = all(
                        self.evaluate_condition(
                            part.strip(),
                            values
                        )
                        for part in parts
                    )

                # ==============================
                # OR LOGIC
                # ==============================
                elif " OR " in condition:

                    parts = condition.split(
                        " OR "
                    )

                    result = any(
                        self.evaluate_condition(
                            part.strip(),
                            values
                        )
                        for part in parts
                    )

                # ==============================
                # SINGLE CONDITION
                # ==============================
                else:

                    result = (
                        self.evaluate_condition(
                            condition,
                            values
                        )
                    )

                if not result:
                    return 0

            return int(
                strategy.get("SCORE", 1)
            )

        except Exception as e:

            print(
                f"TXT evaluator error: {e}"
            )

            return 0
