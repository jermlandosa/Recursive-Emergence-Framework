# Changelog

## v0.9.4 — 2025-08-19
- Codex v2: conventional commits enforcement, auto-version bump, commitment PR truth-event gate

## v0.9c — 2025-08-19
- Added **Codex** repo governance: rules, gates, git hooks, and CI workflow
- New files: `codex/rules.json`, `codex/codex_apply.py`, `codex/VERSION`
- Local hooks installer: `scripts/install_hooks.sh`

## v0.9b — 2025-08-19
- Added zero-dependency local web server and dashboard (`scripts/server.py`, `web/`)
- New endpoints: `GET /`, `POST /ingest`, `GET /state`
- README updated with server instructions
- Added macOS LaunchAgent template for autostart

## v0.9a — 2025-08-19
- **Friction Alarms** with configurable thresholds
- **Truth Events** logger capturing high-impact commitments
- Events persisted to `data/truth_events.jsonl`

## v0.9 — 2025-08-19
- Initial MVP: identity map, truth checks, resonance forecaster, CLI
