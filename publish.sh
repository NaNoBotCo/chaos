#!/bin/bash
# Build the site into docs/, checked. GitHub Pages serves docs/ from main.
#
#   ./publish.sh
#
set -euo pipefail
cd "$(dirname "$0")"
export PYTHONUTF8=1
SITE_URL="${SITE_URL:-https://nanobotco.github.io/chaos}"

STYLE="$HOME/.claude/bin/stylecheck.py"
if [ -f "$STYLE" ]; then
  python3 "$STYLE" tools chaos.py README.md NOTICE.txt || { echo "REFUSED: style. See ~/.claude/STYLE.md"; exit 4; }
fi

python3 tools/figures.py
SITE_URL="$SITE_URL" python3 tools/site.py
python3 tools/card.py
python3 tests/check_links.py || { echo "REFUSED: broken internal links"; exit 3; }
python3 "$STYLE" build/site || { echo "REFUSED: style in built pages"; exit 4; }

# nothing that names this machine may be published
if grep -rl "/Users/" build/site >/dev/null 2>&1; then
  echo "REFUSED: host paths found in build/site"; exit 2
fi

rm -rf docs
cp -R build/site docs
touch docs/.nojekyll
echo "docs/ ← $(find docs -name 'index.html' | wc -l | tr -d ' ') pages, $(du -sh docs | cut -f1)"
