from services.alert_service import AlertService


class TradeRegistry:

    def __init__(self):

        self.alert_service = AlertService()

    def register_alert(
        self,
        market,
        strategy_mode,
        bullish_rank,
        bearish_rank
    ):

        alert_uid = (
            self.alert_service
            .generate_alert_uid()
        )

        self.alert_service.save_alert(

            alert_uid,

            market,

            strategy_mode
        )

        signal_counter = 1

        combined = []

        if not bullish_rank.empty:
            combined.extend(
                bullish_rank.to_dict(
                    "records"
                )
            )

        if not bearish_rank.empty:
            combined.extend(
                bearish_rank.to_dict(
                    "records"
                )
            )

        signal_map = []

        for row in combined:

            signal_uid = (

                f"{alert_uid}-"

                f"S{signal_counter:03d}"
            )

            self.alert_service.save_signal(

                signal_uid,

                alert_uid,

                row,

                strategy_mode
            )

            signal_map.append({

                "signal_uid":
                    signal_uid,

                "symbol":
                    row["symbol"]
            })

            signal_counter += 1

        return (
            alert_uid,
            signal_map
        )
