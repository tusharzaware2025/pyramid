# pyramid

## Cursor Cloud specific instructions

### What this repository is
- The `main` branch is a **documents/data repository**, not a runnable application: it contains a CV PDF, a video (`q.mp4`), a quiz dataset (`questions.csv`), and an Azure→Snowflake deployment runbook (`.docx`). There is no server, web app, database, or build system on `main`.
- The only executable **code** lives on feature branches (e.g. `cursor/exclude-adf-mpe-from-cicd-8f99`): standalone Python CLI utilities under `scripts/` with `unittest` tests under `tests/` that strip ADF Managed Private Endpoints from ARM templates and repoint linked-service integration runtimes for CI/CD.

### Runtime / dependencies
- Everything here needs only **Python 3 (standard library)** — no third-party packages, no lockfiles, no package manifest. Python 3.12 is preinstalled in the Cloud VM, so there is nothing to install. The startup update script is a no-op guard that only installs from `requirements.txt` if one is ever added.

### Lint / test / build / run
- There is no lint or build tooling configured anywhere in the repo.
- Tests (only present on code feature branches) run with the stdlib test runner: `python3 -m unittest discover -s tests -v`.
- The CLI scripts run directly, e.g. `python3 scripts/filter_adf_arm_template.py --help`.
- To exercise code that lives on another branch without leaving your current branch, extract it into a temp dir: `git archive <branch> | tar -x -C /tmp/work && cd /tmp/work`.
