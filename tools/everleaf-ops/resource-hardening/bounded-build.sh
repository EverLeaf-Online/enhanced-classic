#!/bin/sh
set -eu
[ "$#" -gt 0 ] || exit 2
exec systemd-run --wait --pipe --collect --uid=ubuntu --slice=everleaf-build.slice -p RuntimeMaxSec=1800 -p Nice=10 "$@"
