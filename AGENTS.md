# Persistent Codex Instructions

## Project aur environment

- Project: AI Trading Tool for Indian NSE stocks; working branch `main`.
- Shared source of truth for pushed commits: https://github.com/JeetRatanpara28/AI_Treding_Tool.git (`origin`).
- Original upstream: https://github.com/tanmaykaper/Paper-Trading-Bot.git (`upstream`).
- Windows 11, ASUS ROG Strix G15, Ryzen 7, 16 GB RAM, RTX 3050; VS Code + Codex.
- Repository: `C:\AI-Trading-Bot\open-source-bot`.
- Python 3.12 virtual environment: `C:\AI-Trading-Bot\.venv`.
- Interpreter: `C:\AI-Trading-Bot\.venv\Scripts\python.exe`; UTF-8 use karo.
- Large datasets aur results: `E:\AI-Trading-Data`, external exFAT SSD. Drive available hai ya nahi verify karo; existing data preserve karo.
- Existing local launcher `dailytask.bat` use karo; Git Bash compatibility maintain karo.
- Relevant docs padho: `docs/WINDOWS_SETUP.md`, `docs/WINDOWS_RESEARCH.md`, `docs/PUBLICATION.md`.

## User se baat karne ka tareeqa

- Hamesha simple conversational Hinglish mein, Roman letters use karke respond karo.
- Technical terms ka easy Hindi/Hinglish meaning samjhao.
- Code, commands, file paths aur identifiers English mein rakho.
- User se manually command chalwane par ek baar mein sirf ONE PowerShell command do; result aane tak next manual command mat do.
- Authorized tools se safe edits aur tests khud kar sakte ho toh user ko copy-paste karne ko mat bolo.
- Results aur next steps ka clear summary do; user ko separate ChatGPT conversation mein jaane ko mat bolo.

## Trading safety: mandatory

- Sirf paper trading: real capital INR 0. Returns ya profitability kabhi guarantee mat karo.
- Starting simulated capital total INR 100,000: swing INR 33,333.33, intraday INR 33,333.33, momentum INR 33,333.34.
- Live brokerage integrations, real orders, broker login ya broker credentials ki requests NEVER enable karo.
- Fail-closed live-broker guards aur regression tests preserve karo: live request par execution rokna zaroori hai.
- Paid APIs, paid services aur paid connectors avoid karo.
- Automatically trading ya orders send mat karo; trading schedules aur state-pushing GitHub workflows disabled rakho.
- Explicit permission ke bina network downloads mat chalao, including market data aur dependency downloads.
- `--allow-network` flag ko apni taraf se approval mat samjho; user ki explicit permission zaroori hai.
- Private ledgers, journals, historical trading state, personal data aur secrets protect karo.
- Generated market datasets, private portfolio files, credentials, tokens aur `.env` files upload mat karo; `.gitignore` exclusions maintain karo.
- Private simulation `local_research/state/` mein rakho; upstream `state/` ko overwrite ya public mat karo.
- Existing portfolio par `init` dobara mat chalao; pehle offline `status` se check karo.

## Repository workflow aur verification

- Changes se pehle `git status`, current branch/remotes, relevant docs, tests aur current code inspect karo; existing user/Codex changes preserve karo.
- Minimal, reversible changes prefer karo; relevant regression coverage maintain karo.
- Upstream MIT license aur original author Tanmay ki attribution preserve karo.
- `local-upstream-backup*` branches, old portfolio history, ya private data push mat karo; mirror/all-branches pushes mat karo.
- Force-push ya history rewrite mat karo. GitHub push aur destructive operations se pehle user approval lo.
- Is file ko update karne ki permission commit ya push ki permission nahi hai.
- Changes ke baad maintained regression suite chalao, preferably `dailytask.bat test` through the existing launcher.
- Direct equivalent: `C:\AI-Trading-Bot\.venv\Scripts\python.exe -X utf8 -m pytest tests diagnostics -q`.
- Tests bypass, remove ya skip karke failures hide mat karo. Results aur limitations clearly report karo.
- Unqualified pytest discovery mat chalao: archived `legacy/test_*.py` scripts import ke waqt network calls kar sakti hain; separate review aur permission chahiye.
- `scripts/commit_state.sh` project remote par mat chalao bina approval; race tests isko sirf temporary local bare Git repositories ke against exercise karte hain.
- Last reported clean publication commit: `b2b74685c09b680ddd10ec21b7b03236fa48629b`, with 251 maintained tests passed. Yeh historical reference hai; current state verify karo, assume mat karo.

## Agle project goals, isi order mein

1. Simulated portfolio ka offline status verify karo.
2. Sirf explicit approval ke baad small public historical market-data smoke test karo, yani chhota download aur basic verification.
3. Data quality aur market symbol mappings check karo.
4. Realistic transaction costs aur slippage ke saath NSE strategies backtest karo; slippage matlab expected aur simulated execution price ka farq.
5. Look-ahead bias, yani future information ka galti se use, aur overfitting, yani past data par zaroorat se zyada fit hona, avoid karo; buy-and-hold benchmark se compare karo.
6. Robust baseline establish hone ke baad hi AI/ML explore karo.
7. Paper results ke liye local dashboard banao.

Yeh goals roadmap hain, abhi se downloads, trading, dashboard implementation ya external actions shuru karne ki authorization nahi.

## Trading research skill

- Trading concepts, candles/indicators, entry/exit hypotheses, news, risk ya backtest design par kaam karte waqt `skills/nse-paper-research/SKILL.md` use karo; installed naam `$nse-paper-research` hai.
- Is skill mein foundation-to-advanced learning map, primary-source references aur offline arithmetic/timestamp checks hain. Yeh model retraining, certification, guaranteed profit ya complete regulatory knowledge ka claim nahi hai.
- User ki priority: pehle incomplete/failed checks resolve karo, phir naya research phase shuru karo. Failed source ko usable declare mat karo.
- Skill read/install karna strategy parameters badalne, automatic news polling, naye datasets download karne, real orders ya GitHub push ki permission nahi deta.
