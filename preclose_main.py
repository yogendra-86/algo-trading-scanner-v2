import argparse
from pathlib import Path

from config.settings import Settings
from scanner.strategy_loader import load_strategies
from scanner.signal_engine import run_stage_for_market
from utils.logging_utils import get_logger
from services.snapshot import SnapshotService
from services.premium_ranker import PremiumRanker
from services.scanner_gateway import ScannerGateway

logger = get_logger("preclose_main")

market_folder_map = {
    "NSE": "Nse",
    "NASDAQ": "Nasdaq"
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Algo Trading Scanner V2 - Preclose")
    parser.add_argument("--market", required=True, choices=["NSE", "NASDAQ"])
    parser.add_argument("--strategies-dir", default="strategies")
    return parser.parse_args()


# ================================
# SNAPSHOT FILTER (SAFE + FALLBACK)
# ================================
def apply_snapshot_filter(market: str, signals: list) -> list:
    snapshot_service = SnapshotService()
    snapshot = snapshot_service.load_opening_snapshot(market)

    # 🚨 fallback if snapshot missing or empty
    if not snapshot or (
        not snapshot.get("bullish") and not snapshot.get("bearish")
    ):
        logger.warning("⚠️ Snapshot empty or missing → skipping filter")
        return signals

    allowed_symbols = set()

    for item in snapshot.get("bullish", []):
        if isinstance(item, dict):
            allowed_symbols.add(item.get("symbol"))

    for item in snapshot.get("bearish", []):
        if isinstance(item, dict):
            allowed_symbols.add(item.get("symbol"))

    filtered = [
        s for s in signals if s.get("symbol") in allowed_symbols
    ]

    logger.info(
        "Snapshot filter applied | Before=%s After=%s",
        len(signals),
        len(filtered),
    )

    return filtered


# ================================
# MAIN
# ================================
def main() -> None:
    args = parse_args()
    settings = Settings.load()

    project_root = Path(settings.project_root)
    strategies_dir = project_root / args.strategies_dir / market_folder_map[args.market]

    logger.info("Project root: %s", project_root)
    logger.info("Strategies dir: %s", strategies_dir)

    # ================================
    # STEP 1: RUN SCANNER (LIVE STAGE)
    # ================================
    strategies = load_strategies(strategies_dir)

    result = run_stage_for_market(
        market=args.market,
        stage="live",
        strategies=strategies,
        settings=settings,
    )

    logger.info("Scanner execution completed")

    # ================================
    # STEP 2: LOAD SIGNALS FROM CSV
    # ================================
    gateway = ScannerGateway()
    payload = gateway.get_latest_available_scan(args.market, stage="live")

    signals = payload.get("signals", [])
    logger.info("Total signals fetched: %s", len(signals))

    # ================================
    # STEP 3: APPLY SNAPSHOT FILTER
    # ================================
    signals = apply_snapshot_filter(args.market, signals)

    # ================================
    # STEP 4: PREMIUM RANKING
    # ================================
    ranker = PremiumRanker(
        min_price=50 if args.market == "NSE" else 1,
        max_price=2000 if args.market == "NSE" else 500,
        min_rr=1.0,
        top_n=5,
    )

    bullish_top5, bearish_top5 = ranker.get_balanced_top5(signals)

    # ================================
    # STEP 5: FINAL OUTPUT
    # ================================
    print("\n==============================")
    print(f"{args.market} PRE-CLOSE ALERT")
    print("==============================\n")

    # 🟢 Bullish
    print("🟢 Top 5 Bullish Stocks:\n")
    if bullish_top5:
        for i, s in enumerate(bullish_top5, 1):
            print(
                f"{i}. {s.get('symbol')} | "
                f"Score={s.get('premium_score')} | "
                f"RR={s.get('rr')} | "
                f"Entry={s.get('entry')} | "
                f"SL={s.get('sl')} | "
                f"Target={s.get('target')}"
            )
    else:
        print("No bullish signals found")

    # 🔴 Bearish
    print("\n🔴 Top 5 Bearish Stocks:\n")
    if bearish_top5:
        for i, s in enumerate(bearish_top5, 1):
            print(
                f"{i}. {s.get('symbol')} | "
                f"Score={s.get('premium_score')} | "
                f"RR={s.get('rr')} | "
                f"Entry={s.get('entry')} | "
                f"SL={s.get('sl')} | "
                f"Target={s.get('target')}"
            )
    else:
        print("No bearish signals found")

    logger.info("Preclose alert generated successfully")


if __name__ == "__main__":
    main()
