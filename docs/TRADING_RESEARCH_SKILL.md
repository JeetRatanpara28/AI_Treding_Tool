# NSE paper research skill - 7 November 2026

User ne strategy testing se pehle trading knowledge, candle patterns, buy/sell
reasoning, risk aur daily-news research ko persistent skill mein add karne ko kaha.
Is kaam mein bot ki strategy, risk settings, portfolio ya execution code nahi badla.

## Kya add hua

- Source skill: `skills/nse-paper-research/SKILL.md`.
- Installed skill name: `$nse-paper-research`; Codex ki next turn se available.
- Six focused references: learning map, market/risk, setups, news/fundamentals,
  validation aur primary-source register.
- Offline helper: `scripts/research_math.py`; long-position budget arithmetic aur
  timezone-aware news-availability checks. Koi network, broker ya order access nahi.
- `AGENTS.md` mein skill routing add hui; purane rules preserve hue.

Coverage mein 26 foundational-to-advanced topics hain: instrument/horizon,
market mechanics, candles/charts/indicators, entry/exit hypotheses, execution,
costs, risk/portfolio, corporate actions, fundamentals/governance, macro/news,
data quality, bias, benchmarks, statistics, psychology aur AI/ML prerequisites.
Setups reference mein ek complete hypothetical breakout rule card bhi hai;
yeh active strategy ya profitable buy/sell recommendation nahi hai.

## Sources aur limits

Public NSE technical-analysis outline/course description, NISM risk education,
SEBI investor guidance, exchange filing portals, RBI policy archive aur original
research abstracts inspect kiye. Exact links, review date aur access limitations
`references/sources.md` mein hain. Dynamic news-page shell ko live news feed nahi
maana. Paid modules enroll/complete nahi kiye; unread papers ko fully read ya
replicated claim nahi kiya.

Official OpenAI curated skill catalog mein dedicated NSE trading skill listed
nahi thi, isliye reviewed custom skill banayi. Koi random third-party signal bot,
paid connector, broker integration ya extra Python package install nahi hua.

Skill maintained instructions/references hai: underlying model weights retrain
nahi hue, certification nahi mili, aur saare possible future trading/regulatory
rules jaanne ka claim nahi hai. Changing fees, rules aur news ko relevant date
par dobara verify karna hoga. Candle/pattern/sentiment se guaranteed returns nahi.

## Validation

- Official skill-creator structural validator: PASS.
- Relative links, UI metadata, UTF-8 and unfinished-template checks: PASS.
- 17 synthetic arithmetic/timestamp checks: PASS. Cases include cost-aware sizing,
  cash/lot caps, zero-position outcomes, gap risk, negative expectancy despite
  high win rate, post-decision news exclusion and timezone errors.
- Maintained project suite: 342 passed in 40.44 seconds with `dailytask.bat test`.
- Eight documented behavioral competency cases are review expectations, not an
  independent model evaluation or evidence of market profitability.

Learning/install request se live trading, automatic news polling, dataset download,
strategy deployment ya GitHub push ki permission nahi milti. Existing source and
calendar limitations in `docs/REPAIR_STATUS.md` still apply. Is task mein koi naya
strategy backtest, paper-engine run, commit ya push nahi hua.
