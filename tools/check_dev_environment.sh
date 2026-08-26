#!/usr/bin/env bash
set -euo pipefail

failures=0

if ! command -v java >/dev/null 2>&1; then
  echo "ERROR: Java is not installed. Everleaf requires JDK 21."
  failures=$((failures + 1))
else
  java_major="$(java -version 2>&1 | sed -n '1s/.*version "\([0-9]*\).*/\1/p')"
  if [[ "$java_major" != "21" ]]; then
    echo "ERROR: Java $java_major is installed; Everleaf requires JDK 21."
    failures=$((failures + 1))
  fi
fi

if ! command -v javac >/dev/null 2>&1; then
  echo "ERROR: javac is missing. Install a full JDK 21, not a JRE."
  failures=$((failures + 1))
fi

if ! getent hosts repo.maven.apache.org >/dev/null 2>&1; then
  echo "ERROR: Maven Central cannot be resolved from this environment."
  failures=$((failures + 1))
fi

if (( failures > 0 )); then
  echo "Environment check failed with $failures problem(s)."
  exit 1
fi

echo "Environment check passed: JDK 21 compiler and Maven Central are available."
