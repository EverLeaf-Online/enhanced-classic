#!/usr/bin/env bash
set -euo pipefail

WZPY_REPO="https://github.com/Leonana69/wz-python.git"
WZPY_COMMIT="013b47b7ee2903e45d178d3ec6dd320f10e8b713"
WZPY_DIR="${EVERLEAF_WZPY_ROOT:-/opt/everleaf/wz-python}"
CHARACTER_WZ="${EVERLEAF_CHARACTER_WZ:-/opt/everleaf/patches/files/Character.wz}"
UNIT_SOURCE="/opt/everleaf/web/ops/everleaf-wz-avatar.service"
UNIT_TARGET="/etc/systemd/system/everleaf-wz-avatar.service"

if [[ ! -s "$CHARACTER_WZ" ]]; then
  echo "EverLeaf Character.wz is missing or empty: $CHARACTER_WZ" >&2
  exit 1
fi

need_checkout=1
if [[ -d "$WZPY_DIR/.git" ]]; then
  current="$(git -C "$WZPY_DIR" rev-parse HEAD 2>/dev/null || true)"
  if [[ "$current" == "$WZPY_COMMIT" ]]; then
    need_checkout=0
  fi
fi

if [[ "$need_checkout" -eq 1 ]]; then
  stage="$(mktemp -d /tmp/everleaf-wzpy.XXXXXX)"
  cleanup_stage() { rm -rf "$stage"; }
  trap cleanup_stage EXIT
  git clone --quiet --no-checkout "$WZPY_REPO" "$stage"
  git -C "$stage" fetch --quiet --depth 1 origin "$WZPY_COMMIT"
  git -C "$stage" checkout --quiet --detach "$WZPY_COMMIT"
  test "$(git -C "$stage" rev-parse HEAD)" = "$WZPY_COMMIT"

  sudo rm -rf "$WZPY_DIR"
  sudo install -d -m 755 "$(dirname "$WZPY_DIR")"
  sudo mv "$stage" "$WZPY_DIR"
  sudo chown -R "$(id -un):$(id -gn)" "$WZPY_DIR"
  trap - EXIT
fi

if [[ ! -x "$WZPY_DIR/.venv/bin/python" ]]; then
  python3 -m venv "$WZPY_DIR/.venv"
fi

requirements_hash="$(sha256sum "$WZPY_DIR/requirements.txt" | awk '{print $1}')"
stamp="$WZPY_DIR/.venv/.everleaf-requirements-sha256"
installed_hash="$(cat "$stamp" 2>/dev/null || true)"
if [[ "$installed_hash" != "$requirements_hash" ]]; then
  "$WZPY_DIR/.venv/bin/python" -m pip install --disable-pip-version-check --quiet -r "$WZPY_DIR/requirements.txt"
  printf '%s\n' "$requirements_hash" > "$stamp"
fi

sudo install -m 644 "$UNIT_SOURCE" "$UNIT_TARGET"
sudo systemctl daemon-reload
sudo systemctl enable everleaf-wz-avatar.service >/dev/null
sudo systemctl restart everleaf-wz-avatar.service

probe="$(mktemp /tmp/everleaf-avatar-probe.XXXXXX.png)"
cleanup_probe() { rm -f "$probe"; }
trap cleanup_probe EXIT
ready=0
for _ in $(seq 1 30); do
  if curl --fail --silent --show-error --max-time 20 \
      --output "$probe" \
      "http://127.0.0.1:3011/api/character/compose?ids=00002000%2C00012000%2C00030020%2C00020000&pose=stand1&frame=0&scale=2"; then
    if python3 - "$probe" <<'PY'
import pathlib, sys
p = pathlib.Path(sys.argv[1])
data = p.read_bytes()
raise SystemExit(0 if len(data) >= 100 and data[:8] == b"\x89PNG\r\n\x1a\n" else 1)
PY
    then
      ready=1
      break
    fi
  fi
  sleep 2
done

if [[ "$ready" -ne 1 ]]; then
  sudo systemctl status everleaf-wz-avatar.service --no-pager || true
  sudo journalctl -u everleaf-wz-avatar.service -n 100 --no-pager || true
  echo "EverLeaf local Character.wz renderer did not become healthy." >&2
  exit 1
fi

systemctl is-active --quiet everleaf-wz-avatar.service
bytes="$(wc -c < "$probe")"
echo "EverLeaf local v83 WZ avatar renderer is healthy (${bytes} byte probe)."
