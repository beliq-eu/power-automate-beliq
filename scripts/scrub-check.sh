#!/usr/bin/env bash
# Fail if an em-dash (U+2014) appears in any definition, docs or example.
# Org rule: no em-dashes in published / customer-facing text.
# The character is built from its codepoint rather than written out, so this
# file is not itself a hit when scripts/ is scanned.
set -euo pipefail

emdash=$(printf '\u2014')
targets=(Beliq example-flows scripts README.md SUBMISSION.md .github)
existing=()
for t in "${targets[@]}"; do
  [ -e "$t" ] && existing+=("$t")
done

if grep -rn -- "$emdash" "${existing[@]}"; then
  echo "em-dash (U+2014) found in the files above; remove it before publishing."
  exit 1
fi
echo "no em-dash found"
