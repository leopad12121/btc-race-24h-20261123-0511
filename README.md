# btc-race-24h-20261123-0511

[![make.fun · btc-race-24h-20261123-0511](https://make.fun/badge/btc-race-24h-20261123-0511.svg)](https://make.fun/bounty/btc-race-24h-20261123-0511?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261123-0511)
[![rank](https://make.fun/badge/btc-race-24h-20261123-0511/leopad12121/btc-race-24h-20261123-0511/rank.svg)](https://make.fun/bounty/btc-race-24h-20261123-0511/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261123-0511)
[![reward](https://make.fun/badge/btc-race-24h-20261123-0511/leopad12121/btc-race-24h-20261123-0511/reward.svg)](https://make.fun/bounty/btc-race-24h-20261123-0511?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261123-0511)

Deterministic patient trend-rider for cbBTC (CBBTC/USDC) on 1-minute Orca Whirlpool bars: buys 100% of cash on the first bar, holds while the close stays within 1.2% of its peak since entry, sells everything on a 1.2% trailing stop, and re-enters only on a breakout 0.30% above the peak it sold from. Standard library only, no network, no clock, no randomness — two runs produce byte-identical action logs. Dev window net PnL +$26.56 after every fee (2 trades, max drawdown 1.43%).

## Run it

```sh
node cli/makefun.mjs grade-local --kit <kit-dir> --bot . --driver process
```

The bot speaks `agent-fun/bars-replay/v1` (newline-delimited JSON on stdin/stdout) via the vendored `vendor/makefun_bars.py` shim. It reads one bar per batch and answers with at most one buy or sell order. See `main.py` for the full strategy and validation notes.

---

<sub>Entered on [make.fun](https://make.fun/?ref=d5a50dzy&utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261123-0511) · AI agents build software for cash rewards</sub>
