## Repo Status (Python-only, Pixi-managed)

### Overview
- Upstream: `https://github.com/firekultur/fluxgym`
- Working branch: `firekultur` (pushed to origin)
- Goal: run Fluxgym locally without Docker, using Pixi and CPU-friendly deps.

### Done
- Git
  - Created and pushed branch `firekultur`.
  - Added `.gitignore` entries for Pixi and `security_reports/`.
  - Added `.cursorignore` to avoid indexing heavy/generated assets.
- Docker → archived
  - Moved `Dockerfile`, `Dockerfile.cuda12.4`, `docker-compose.yml`, `.dockerignore` to `_backup/` with a README.
- Environment (Pixi)
  - Added `pixi.toml` with project deps (CPU-friendly PyTorch) and security tools.
  - Installed Pixi env (`pixi install`).
- Security
  - Added `scripts/security_scan.py` (bandit, pip-audit, safety, semgrep, detect-secrets).
  - Ran initial scan; reports saved under `security_reports/<timestamp>/` (ignored by git).
    - bandit: large volume of findings (JSON saved).
    - pip-audit: 0 vulns.
    - safety: report saved.
    - semgrep: 0 findings.
    - detect-secrets: 0 findings.
- sd-scripts
  - Cloned `kohya-ss/sd-scripts` (branch `sd3`) into `sd-scripts/`.
  - Created `sd-scripts/requirements-macos.txt` (excludes `bitsandbytes`).
  - Installed macOS/CPU-friendly deps with Pixi (some version pin downgrades; see notes below).

### Notes / Conflicts
- `peft` requires `huggingface_hub>=0.25.0` but `sd-scripts` pins `0.24.5`. App may still work; we can bump `huggingface_hub` if needed.
- `semgrep` prefers `rich~=13.5.2`; sd-scripts installs `rich==13.7.0`. Non-blocking for now.

### To do before starting the app
- Optional: resolve `huggingface_hub` pin by upgrading to `>=0.25.0` if runtime errors appear.
- Verify base model autoload works (downloads to `models/` on first run).
- Sanity check: generate `train` script via UI and ensure `sd-scripts` entry points callable.

### How to run (manual)
1) Install env (already done, re-run if needed):
```
pixi install
```
2) Install sd-scripts deps (already done):
```
pixi run python3 -m pip install -r sd-scripts/requirements-macos.txt --no-input
```
3) Start the app (user starts it manually):
```
pixi run python3 app.py
```
Open: http://localhost:7860

### Maintenance
- Re-run security scan anytime:
```
pixi run python3 scripts/security_scan.py
```


