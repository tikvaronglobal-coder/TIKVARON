#!/usr/bin/env bash
set -euo pipefail

# Installs the upstream TIKVARON-approved Trader + Instagram skill packs.
# Skills are copied as data/instructions; no trading or Instagram action is run.

TRADER_REPO="https://github.com/Jakeschincariol/trader-skill.git"
TRADER_COMMIT="5189e79b9a480755a3733ac9713f5353981dbe18"
INSTAGRAM_REPO="https://github.com/Jakeschincariol/instagram-agent-skill.git"
INSTAGRAM_COMMIT="d03c56bb598be770c60b201f94237e5d1a4268a6"

SCOPE="project"
CHECK_ONLY=0
while (($#)); do
  case "$1" in
    --scope) SCOPE="${2:?Missing value for --scope}"; shift 2 ;;
    --check) CHECK_ONLY=1; shift ;;
    -h|--help)
      echo "Usage: $0 [--scope project|user] [--check]"
      exit 0 ;;
    *) echo "Unknown option: $1" >&2; exit 2 ;;
  esac
done
[[ "$SCOPE" == "project" || "$SCOPE" == "user" ]] || {
  echo "--scope must be project or user" >&2; exit 2;
}

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
if [[ "$SCOPE" == "project" ]]; then
  DEST="$ROOT/.agents/skills"
else
  DEST="$HOME/.agents/skills"
fi

command -v git >/dev/null || { echo "git is required" >&2; exit 1; }
command -v python3 >/dev/null || { echo "Python 3 is required" >&2; exit 1; }

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

clone_pinned() {
  local url="$1" commit="$2" dir="$3"
  git clone --quiet --filter=blob:none --no-checkout "$url" "$dir"
  git -C "$dir" checkout --quiet --detach "$commit"
  local actual
  actual="$(git -C "$dir" rev-parse HEAD)"
  [[ "$actual" == "$commit" ]] || {
    echo "Pinned revision mismatch for $url" >&2; exit 1;
  }
}

clone_pinned "$TRADER_REPO" "$TRADER_COMMIT" "$TMP/trader"
clone_pinned "$INSTAGRAM_REPO" "$INSTAGRAM_COMMIT" "$TMP/instagram"

python3 - "$TMP/trader" "$TMP/instagram" <<'PY'
import pathlib, sys, py_compile
trader, instagram = map(pathlib.Path, sys.argv[1:])
trader_skills = sorted(p for p in trader.glob("trader-*") if (p / "SKILL.md").is_file())
instagram_skills = sorted(p for p in (instagram / "skills").glob("ig-*") if (p / "SKILL.md").is_file())
assert len(trader_skills) == 11, f"Expected 11 trader skills, found {len(trader_skills)}"
assert len(instagram_skills) == 13, f"Expected 13 Instagram skills, found {len(instagram_skills)}"
for folder in trader_skills + instagram_skills:
    skill = folder / "SKILL.md"
    data = skill.read_text(encoding="utf-8")
    assert data.startswith("---\n") and "\nname:" in data and "\ndescription:" in data, f"Invalid skill metadata: {skill}"
for source in list(trader.rglob("*.py")) + list(instagram.rglob("*.py")):
    py_compile.compile(str(source), doraise=True)
print(f"Validated {len(trader_skills)} trader skills and {len(instagram_skills)} Instagram skills; Python syntax checks passed.")
PY

if [[ "$CHECK_ONLY" -eq 1 ]]; then
  (cd "$TMP/trader" && python3 -m unittest discover -s tests -v)
  echo "Validation-only run passed. Nothing was installed."
  exit 0
fi

mkdir -p "$DEST"
for folder in "$TMP"/trader/trader-* "$TMP"/instagram/skills/ig-*; do
  [[ -f "$folder/SKILL.md" ]] || continue
  name="$(basename "$folder")"
  if [[ -e "$DEST/$name" ]]; then
    echo "Refusing to overwrite existing skill: $DEST/$name" >&2
    echo "Back it up or remove it deliberately, then rerun." >&2
    exit 1
  fi
done

for folder in "$TMP"/trader/trader-* "$TMP"/instagram/skills/ig-*; do
  [[ -f "$folder/SKILL.md" ]] || continue
  cp -a "$folder" "$DEST/$(basename "$folder")"
done
POLICY_SRC="$(cd "$(dirname "$0")/../.agents/skills/tikvaron-approval-policy" && pwd)"
POLICY_DEST="$DEST/tikvaron-approval-policy"
if [[ "$POLICY_SRC" != "$POLICY_DEST" ]]; then
  if [[ -e "$POLICY_DEST" ]]; then
    echo "Refusing to overwrite existing policy skill: $POLICY_DEST" >&2
    exit 1
  fi
  cp -a "$POLICY_SRC" "$DEST/"
fi

echo "Installed 24 upstream skills plus TIKVARON approval policy into: $DEST"
echo "No credentials, broker connectors, Instagram logins, or publishing integrations were installed."
echo "For an additional hard block, see docs/AGENT-SKILLS-SETUP.md before enabling trader-broker."
