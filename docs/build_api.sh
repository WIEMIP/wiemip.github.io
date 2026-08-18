#!/bin/bash
# Generate the API reference at /docs/api with pdoc, from the registry's own source.
#
#   bash docs/build_api.sh
#
# pdoc imports wiemip_registry, so it needs the registry's dependencies — hence
# `uv run` inside that repo rather than here. Output is committed; GitHub Pages
# serves it as-is. Re-run after changing docstrings.
set -euo pipefail

SITE_ROOT=$(cd "$(dirname "$0")/.." && pwd)
REGISTRY_REPO=${REGISTRY_REPO:-$SITE_ROOT/../wiemip-data-processing}
OUT=$SITE_ROOT/docs/api
SOURCE=https://github.com/WIEMIP/wiemip-data-registry/blob/main/wiemip_registry/

if [[ ! -d $REGISTRY_REPO ]]; then
    echo "registry repo not found at $REGISTRY_REPO (override with \$REGISTRY_REPO)" >&2
    exit 1
fi

cd "$REGISTRY_REPO"
uv run --with pdoc pdoc wiemip_registry \
    --output-directory "$OUT" \
    --docformat markdown \
    --edit-url "wiemip_registry=$SOURCE" \
    --logo /assets/logo_small.png \
    --logo-link /docs/api/ \
    --favicon /assets/favicon-32.png \
    --footer-text "WIEMIP · wiemip_registry" \
    --template-directory "$SITE_ROOT/docs/pdoc-templates"

echo "wrote $OUT ($(find "$OUT" -name '*.html' | wc -l | tr -d ' ') pages)"
