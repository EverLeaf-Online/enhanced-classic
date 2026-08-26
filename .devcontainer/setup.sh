#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

chmod +x mvnw
bash tools/check_dev_environment.sh

echo "Warming the Everleaf Maven cache and compiling test sources..."
./mvnw -B -DskipTests test-compile

echo "Everleaf development container is ready."
