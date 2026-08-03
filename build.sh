#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

export PATH="${HOME}/Library/Python/3.9/bin:${PATH}"

VERSION="${1:-1.3.0}"
PYTHON_BIN="${PYTHON_BIN:-python3.12}"
if ! command -v "${PYTHON_BIN}" >/dev/null 2>&1; then
  PYTHON_BIN="python3"
fi

# Prevent .pyc creation during tests and ucc-gen; AppInspect rejects compiled Python.
export PYTHONDONTWRITEBYTECODE=1

clean_bytecode() {
  local target="$1"
  find "${target}" -type d -name __pycache__ -prune -exec rm -rf {} + 2>/dev/null || true
  find "${target}" -name '*.pyc' -delete 2>/dev/null || true
  find "${target}" -name '*.pyo' -delete 2>/dev/null || true
}

echo "==> Cleaning bytecode from package source"
clean_bytecode package

echo "==> Generating Claude app icons"
"${PYTHON_BIN}" scripts/generate_app_icons.py

echo "==> Running unit tests"
"${PYTHON_BIN}" -m unittest discover -s tests/unit -p "test_*.py"
clean_bytecode package

UCC_GEN="${UCC_GEN:-ucc-gen}"
if ! command -v "${UCC_GEN}" >/dev/null 2>&1; then
  if [[ -x "${ROOT}/.build-venv/bin/ucc-gen" ]]; then
    UCC_GEN="${ROOT}/.build-venv/bin/ucc-gen"
  fi
fi

echo "==> Building TA-anthropic_claude_enterprise v${VERSION} (${PYTHON_BIN})"
"${UCC_GEN}" build --ta-version "${VERSION}" --python-binary-name "${PYTHON_BIN}"

echo "==> Removing bytecode from build output (pre-package)"
clean_bytecode "output/TA-anthropic_claude_enterprise"

echo "==> Post-build verification"
"${PYTHON_BIN}" - <<PY
from pathlib import Path

app_root = Path("output/TA-anthropic_claude_enterprise")
app_conf = app_root / "default/app.conf"
text = app_conf.read_text()
if "reload.inputs" in text:
    raise SystemExit(
        "app.conf must not contain reload.inputs in [triggers]; "
        "inputs.conf is Splunk-defined (AppInspect check_for_trigger_stanza)."
    )

inputs_conf = app_root / "default/inputs.conf"
inputs_text = inputs_conf.read_text()
required = {
    "compliance_activities": "compliance_activities.py",
    "compliance_directory": "compliance_directory.py",
    "compliance_content": "compliance_content.py",
    "analytics_reports": "analytics_reports.py",
}
for stanza, script in required.items():
    block = f"[{stanza}]"
    if block not in inputs_text:
        raise SystemExit(f"Missing inputs.conf stanza: {stanza}")
    section = inputs_text.split(block, 1)[1].split("\n[", 1)[0]
    if f"script = {script}" not in section:
        raise SystemExit(f"Missing script = {script} in [{stanza}] stanza")
    if "python.required = 3.13" not in section:
        raise SystemExit(f"Missing python.required = 3.13 in [{stanza}] stanza")

for script in app_root.glob("bin/*.py"):
    if script.name.startswith("TA-anthropic_claude_enterprise_rh_"):
        continue
    script.chmod(script.stat().st_mode | 0o111)

web_conf = app_root / "default/web.conf"
web_text = web_conf.read_text()
if "[settings]" in web_text:
    blocks = []
    skip = False
    for line in web_text.splitlines():
        if line.strip().startswith("[") and line.strip().endswith("]"):
            skip = line.strip() == "[settings]"
        if not skip:
            blocks.append(line)
    web_conf.write_text("\n".join(blocks).rstrip() + "\n")
    web_text = web_conf.read_text()

allowed_stanza_prefixes = ("[expose:", "[endpoint:")
for line in web_text.splitlines():
    stripped = line.strip()
    if stripped.startswith("[") and stripped.endswith("]"):
        if not any(stripped.startswith(prefix) for prefix in allowed_stanza_prefixes):
            raise SystemExit(
                f"web.conf stanza {stripped!r} is not allowed for AppInspect check_web_conf"
            )

pyc_files = list(app_root.rglob("*.pyc")) + list(app_root.rglob("*.pyo"))
pycache_dirs = list(app_root.rglob("__pycache__"))
if pyc_files or pycache_dirs:
    raise SystemExit(
        "Compiled Python artifacts remain in output before packaging: "
        f"{len(pycache_dirs)} __pycache__ dirs, {len(pyc_files)} .pyc/.pyo files"
    )

static_dir = app_root / "static"
appserver_static = app_root / "appserver/static"
if static_dir.is_dir():
    appserver_static.mkdir(parents=True, exist_ok=True)
    for icon in static_dir.glob("appIcon*.png"):
        target = appserver_static / icon.name
        target.write_bytes(icon.read_bytes())
PY

echo "==> Packaging"
"${UCC_GEN}" package --path output/TA-anthropic_claude_enterprise

echo "==> Verifying package excludes bytecode"
"${PYTHON_BIN}" - <<PY
import tarfile
from pathlib import Path

tarball = Path("TA-anthropic_claude_enterprise-${VERSION}.tar.gz")
if not tarball.is_file():
    raise SystemExit(f"Expected tarball not found: {tarball}")
with tarfile.open(tarball, "r:gz") as archive:
    names = archive.getnames()
    bad = [
        name
        for name in names
        if "/__pycache__/" in name or name.endswith((".pyc", ".pyo"))
    ]
    if bad:
        raise SystemExit(f"Package contains compiled Python files: {bad[:10]}")
    for required_icon in (
        "TA-anthropic_claude_enterprise/static/appIcon.png",
        "TA-anthropic_claude_enterprise/appserver/static/appIcon.png",
    ):
        if required_icon not in names:
            raise SystemExit(f"Package missing required icon: {required_icon}")
print(f"Verified {tarball.name} has no .pyc/.pyo/__pycache__ and includes app icons")
PY

echo "==> Done: TA-anthropic_claude_enterprise-${VERSION}.tar.gz"
