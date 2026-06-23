#!/usr/bin/env bash
# Publica as 4 issues do PRD de posters no GitHub (bytols/TCC).
# Pré-requisito: `gh auth login`  (ou GH_TOKEN/GITHUB_TOKEN no ambiente).
set -euo pipefail

cd "$(dirname "$0")"
REPO="bytols/TCC"
LABEL="ready-for-agent"

# 1. Garante o label de triagem
gh label create "$LABEL" --repo "$REPO" --color 0E8A16 \
  --description "Pronto para agente AFK" 2>/dev/null || true

new_issue () {  # $1 = arquivo .md  →  ecoa o número da issue criada
  local file="$1"
  local title; title="$(sed -n 's/^# //p' "$file" | head -1)"
  local url;   url="$(gh issue create --repo "$REPO" \
                        --title "$title" \
                        --body-file "$file" \
                        --label "$LABEL")"
  echo "${url##*/}"
}

# 2. Slice 1 (sem bloqueio) — captura o número p/ referenciar nas demais
N1="$(new_issue 01-resolver-manifest-report.md)"
echo "Slice 1 → #$N1"

# 3. Slices 2 e 4 dependem da 1; Slice 3 depende da 2.
#    Reescreve o "Blocked by" com o número real antes de publicar.
publish_blocked () {  # $1 = arquivo  $2 = texto do blocker
  local file="$1" blocker="$2" tmp
  tmp="$(mktemp)"
  awk -v b="$blocker" '
    /^## Blocked by/ {print; print ""; print "- " b; skip=1; next}
    skip && /^## / {skip=0}
    skip {next}
    {print}
  ' "$file" > "$tmp"
  local title; title="$(sed -n 's/^# //p' "$file" | head -1)"
  local url; url="$(gh issue create --repo "$REPO" \
                      --title "$title" --body-file "$tmp" --label "$LABEL")"
  rm -f "$tmp"
  echo "${url##*/}"
}

N2="$(publish_blocked 02-catalog-serving-filter.md "#$N1 — Resolvedor de posters")"
echo "Slice 2 → #$N2"
N4="$(publish_blocked 04-verify-script.md "#$N1 — Resolvedor de posters")"
echo "Slice 4 → #$N4"
N3="$(publish_blocked 03-frontend-local-poster.md "#$N2 — Catálogo servido só com filmes verificados")"
echo "Slice 3 → #$N3"

echo "Pronto: #$N1 (1) → #$N2 (2) → #$N3 (3),  #$N4 (4) depende de #$N1."
