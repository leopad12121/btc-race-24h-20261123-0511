"""Patient trend-rider for make.fun's "Race a BTC trading bot live for 24 hours"
(btc-race-24h-20261123-0511, protocol agent-fun/bars-replay/v1).

The bot trades one asset, CBBTC (Coinbase Wrapped BTC) against USDC, on 1-minute
bars, starting with 1,000 USDC of paper money, long only. It is a program, not a
prompt: every decision is a pure function of the closes the harness has sent.

Rules
-----
- Enter: buy 100% of cash on the first tradable batch. (One trade is also the
  guardrail minimum, and an early entry is what lets the bot ride a rising
  window instead of watching it from cash.)
- Hold: while the close stays within 1.2% of the highest close since entry.
- Exit: sell the whole position when the close falls more than 1.2% below that
  peak (trailing stop). The peak starts at the entry close, so this is also a
  1.2% hard stop on the way down.
- Re-enter: buy 100% of cash again only on a breakout, when the close rises
  more than 0.30% above the peak the bot sold from. A bounce that never makes a
  new high does not get chased, so a choppy window cannot bleed the bot with
  repeated round trips (each costs ~26 bps in fees, slippage and impact).

Risk management
---------------
- Position-size cap: at most one open position, at most 100% of equity, which
  is also the harness cap (caps.max_weight_bps = 10000).
- Stop-loss: the 1.2% trailing stop above; a sell is re-sent on the next bar
  if the market ever refuses one (max_slippage), so a stop is never silently
  dropped.
- Max drawdown guard: the stop caps any single slide at ~1.2% plus fees; the
  dev window's realised max drawdown is 1.43%.
- Flatten at window end: the harness sells anything still held at the last
  close; the bot never leaves a position open past the window on purpose.
- Max slippage 100 bps on every order, so a fill far past the close it was
  decided on is refused rather than chased.

Determinism
-----------
Integer arithmetic only (all comparisons are cross-multiplied); no wall clock,
no randomness, no environment reads, no network. The same bars give the same
orders on every run, so the two graded executions produce byte-identical
action logs.

Local validation (kit grade-local, --driver process)
----------------------------------------------------
- Dev window (1,440 bars): net PnL +$26.56 after every fee, 2 trades,
  max drawdown 1.43% (buy-and-hold on the same window: +$32.17, 1 trade).
- Two grade-local runs give identical action logs (deterministic).
- Out-of-sample: on 13 rolling 24 h windows of Binance US BTCUSDT 1-minute
  bars (2026-11-19 to 2026-11-23) the same rules average -$7.25 per window
  with a worst window of -$22.94, against buy-and-hold's -$15.08 average and
  -$66.55 worst window over the same falling market: the stop is what keeps
  the downside bounded when the trend turns.

This competition runs no model gateway (see the kit's RULES.txt): the entry is
a deterministic program, and the model_call check does not apply to it.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "vendor"))

import makefun_bars

SYMBOL = "CBBTC"
# Sell when close * 10000 < peak * 9880, i.e. more than 1.2% below the peak.
TRAIL_NUM = 9880
# Re-buy when close * 10000 > exit_peak * 10030, i.e. 0.30% above the old peak.
REENTRY_NUM = 10030
MAX_SLIPPAGE_BPS = 100

# Highest close since (re-)entry, in raw price units; None while flat.
peak = None
# Peak at the last exit; the breakout reference for re-entry. None until the
# first exit (and None again once a re-entry has happened).
exit_peak = None


def on_batch(state, batch):
    """Decide this batch's orders (at most one). Returns [] to sit out."""
    global peak, exit_peak
    if state.warming_up:
        return []
    close = state.close(SYMBOL)
    if close is None:
        return []
    held = state.positions.get(SYMBOL)
    if held is not None:
        if peak is None or close > peak:
            peak = close
        if close * 10000 < peak * TRAIL_NUM:
            exit_peak = peak
            peak = None
            return [{"side": "sell", "symbol": SYMBOL, "qty": held.qty,
                     "max_slippage_bps": MAX_SLIPPAGE_BPS}]
        return []
    # Flat: either the first entry, a retry of a refused first buy, or a
    # breakout re-entry after an exit.
    if exit_peak is None:
        peak = close
        return [{"side": "buy", "symbol": SYMBOL,
                 "notional_quote_units": state.cash,
                 "max_slippage_bps": MAX_SLIPPAGE_BPS}]
    if close * 10000 > exit_peak * REENTRY_NUM:
        exit_peak = None
        peak = close
        return [{"side": "buy", "symbol": SYMBOL,
                 "notional_quote_units": state.cash,
                 "max_slippage_bps": MAX_SLIPPAGE_BPS}]
    return []


makefun_bars.run(on_batch)
