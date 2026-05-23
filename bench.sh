#!/usr/bin/env bash
# Benchmark ty 0.0.38 vs 0.0.39 against the TypedDict-union + dict() pattern.
#
# Usage:
#   ./bench.sh            # runs the default matrix
#   ./bench.sh 19 8       # single point: 19 variants × 8 keys
#
# Requires `uv` on PATH (https://docs.astral.sh/uv/).

set -euo pipefail
export LC_ALL=C  # force '.' as decimal separator for printf

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

run_one() {
    local version="$1"
    local n="$2"
    local k="$3"
    local out="$SCRIPT_DIR/gen_${n}_${k}.py"
    python3 "$SCRIPT_DIR/generate.py" "$n" "$k" "$out"
    local start end dur rc
    start=$(date +%s.%N)
    timeout 120 uvx "ty@${version}" check "$out" >/dev/null 2>&1 && rc=0 || rc=$?
    end=$(date +%s.%N)
    dur=$(echo "$end - $start" | bc)
    printf "ty %s  n=%2d k=%d  rc=%-3d %.2fs\n" "$version" "$n" "$k" "$rc" "$dur"
}

if [[ $# -ge 2 ]]; then
    run_one 0.0.38 "$1" "$2"
    run_one 0.0.39 "$1" "$2"
    exit 0
fi

echo "=== ty 0.0.38 ==="
for n in 4 8 12 16 19; do
    for k in 1 3 5 8; do
        run_one 0.0.38 "$n" "$k"
    done
done

echo ""
echo "=== ty 0.0.39 ==="
for n in 4 8 12 16 19; do
    for k in 1 3 5 8; do
        run_one 0.0.39 "$n" "$k"
    done
done

rm -f "$SCRIPT_DIR"/gen_*_*.py
