from strategies.entry.bullish.breakout import breakout_entry
from strategies.entry.bullish.vwap_strength import vwap_strength
from strategies.entry.bullish.pullback import pullback_entry

from strategies.entry.bearish.breakdown import breakdown_entry
from strategies.entry.bearish.vwap_weakness import vwap_weakness
from strategies.entry.bearish.pullback import pullback_sell

BULLISH_STRATEGIES = [
    breakout_entry,
    vwap_strength,
    pullback_entry
]

BEARISH_STRATEGIES = [
    breakdown_entry,
    vwap_weakness,
    pullback_sell
]
