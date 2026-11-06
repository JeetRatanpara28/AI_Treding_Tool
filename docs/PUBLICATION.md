# Safe source publication ? 6 November 2026

Destination: https://github.com/JeetRatanpara28/AI_Treding_Tool

The original MIT license, copyright (c) 2026 Tanmay, and upstream attribution
are retained. Original source files and Codex Windows/paper-only changes are
included. Runtime private state, old CSV journals, market data, caches, logs,
credentials, and generated portfolio charts are excluded by `.gitignore`.
The original README portfolio block is backed up locally under ignored
`local_research/upstream-original/README.md`; the published README has a neutral
local-research notice and links to Windows setup.

Publication uses a new root commit, without upstream commit ancestry. This avoids
uploading portfolio blobs from old commits. Original history remains reachable
locally on `local-upstream-backup-20261106`; original data files remain on disk.
`upstream` points to https://github.com/tanmaykaper/Paper-Trading-Bot.git and
`origin` points to the new destination. Only main is intended for upload; never
push the backup branch, tags, or use a mirror push. No force push is used.

Original workflows are preserved in `docs/archived-workflows/*.disabled`.
Their existing scheduling assertions continue to run against those archives.
Active trading workflows are manual-only, unconditionally disabled, read-only,
and contain no trading, secret, or state-pushing steps. The manual research
workflow runs offline tests only. New tests guard these publication requirements.
Live broker/login access remains disabled; no broker credentials are needed.

Windows setup: [WINDOWS_SETUP.md](WINDOWS_SETUP.md). The new `init` command creates
INR 100,000 virtual capital and refuses existing state. On the original workstation
the portfolio is already initialized. Private ledgers are never published.

Validation: maintained offline suite through the exact configured Python 3.12
virtual environment; Git Bash race test retained; initializer overwrite-refusal
and automation-disablement regression coverage added. See the final publication
summary for the verified suite count and remote commit SHA. Archived legacy
import-time integration scripts remain outside the maintained CI suite.
