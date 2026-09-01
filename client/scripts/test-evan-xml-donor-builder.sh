#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
work="${RUNNER_TEMP:-/tmp}/everleaf-evan-xml-donor-test"
libwz="$work/libwz"
build="$work/build"
fixture="$work/fixture/Evan"
donor="$work/donor"

rm -rf "$work"
mkdir -p \
  "$fixture/Skill/Dragon" \
  "$fixture/Character/Dragon" \
  "$fixture/UI" \
  "$fixture/String" \
  "$donor"

# 1x1 PNG. This exercises the same canvas basedata path used by the real Evan XML export.
png='iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAusB9Y9ZlT8AAAAASUVORK5CYII='

cat > "$fixture/Skill/2001.img.xml" <<XML
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<imgdir name="2001.img">
  <imgdir name="skill">
    <imgdir name="20011000">
      <int name="maxLevel" value="3"/>
      <canvas name="icon" basedata="$png">
        <vector name="origin" x="0" y="0"/>
      </canvas>
    </imgdir>
  </imgdir>
</imgdir>
XML

cat > "$fixture/Skill/Dragon/2200.img.xml" <<XML
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<imgdir name="2200.img">
  <imgdir name="skill">
    <imgdir name="22000000">
      <int name="maxLevel" value="20"/>
      <string name="fixture" value="dragon"/>
    </imgdir>
  </imgdir>
</imgdir>
XML

cat > "$fixture/Character/00002000.img.xml" <<XML
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<imgdir name="00002000.img">
  <canvas name="stand1" basedata="$png">
    <vector name="origin" x="0" y="0"/>
  </canvas>
</imgdir>
XML

cat > "$fixture/Character/Dragon/01942000.img.xml" <<XML
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<imgdir name="01942000.img">
  <canvas name="stand" basedata="$png"/>
</imgdir>
XML

cat > "$fixture/UI/Basic.img.xml" <<XML
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<imgdir name="Basic.img">
  <canvas name="EvanFixture" basedata="$png"/>
</imgdir>
XML

cat > "$fixture/UI/UIWindow.img.xml" <<XML
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<imgdir name="UIWindow.img">
  <imgdir name="EvanFixture">
    <int name="enabled" value="1"/>
  </imgdir>
</imgdir>
XML

cat > "$fixture/String/Skill.img.xml" <<'XML'
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<imgdir name="Skill.img">
  <imgdir name="20011000">
    <string name="name" value="Three Snails"/>
    <string name="desc" value="EverLeaf fixture"/>
  </imgdir>
</imgdir>
XML

git clone --quiet https://github.com/toyobayashi/libwz.git "$libwz"
git -C "$libwz" checkout --quiet 41cd5d62ecd229f0eb425c2654ecf0bf8b435d7f

cmake -S "$repo_root/client/tools/evan-xml-donor-builder" -B "$build" \
  -DLIBWZ_SOURCE="$libwz" \
  -DCMAKE_BUILD_TYPE=Release
cmake --build "$build" --config Release --parallel 2

builder="$build/everleaf-evan-xml-donor-builder"
if [[ ! -x "$builder" ]]; then
  builder="$(find "$build" -type f -name everleaf-evan-xml-donor-builder -perm -111 -print -quit)"
fi
test -n "$builder"

"$builder" "$fixture" "$donor"
"$builder" --verify "$donor"

for wz in Skill Character UI String; do
  test -s "$donor/$wz.wz"
done

echo "EverLeaf Evan XML donor builder synthetic round-trip: PASS"
