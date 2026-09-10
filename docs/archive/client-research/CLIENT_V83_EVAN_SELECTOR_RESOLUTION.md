# v83 Evan selector resolution

## Live RaceSelect tree
- `/Login.img/RaceSelect` -> `BtSelect, knight, normal, aran, aran1, textGL`
- `/Login.img/RaceSelect/BtSelect` -> `normal, mouseOver, pressed, disabled`
- `/Login.img/RaceSelect/BtSelect/normal` -> ``
- `/Login.img/RaceSelect/BtSelect/mouseOver` -> ``
- `/Login.img/RaceSelect/BtSelect/pressed` -> ``
- `/Login.img/RaceSelect/BtSelect/disabled` -> ``
- `/Login.img/RaceSelect/knight` -> `text, BtKnight, OnAnimation, OffAnimation`
- `/Login.img/RaceSelect/knight/text` -> ``
- `/Login.img/RaceSelect/knight/BtKnight` -> `normal, mouseOver, pressed, disabled`
- `/Login.img/RaceSelect/knight/BtKnight/normal` -> ``
- `/Login.img/RaceSelect/knight/BtKnight/mouseOver` -> ``
- `/Login.img/RaceSelect/knight/BtKnight/pressed` -> ``
- `/Login.img/RaceSelect/knight/BtKnight/disabled` -> ``
- `/Login.img/RaceSelect/knight/OnAnimation` -> ``
- `/Login.img/RaceSelect/knight/OffAnimation` -> ``
- `/Login.img/RaceSelect/normal` -> `text, BtNormal, OnAnimation, OffAnimation`
- `/Login.img/RaceSelect/normal/text` -> ``
- `/Login.img/RaceSelect/normal/BtNormal` -> `normal, mouseOver, pressed, disabled`
- `/Login.img/RaceSelect/normal/BtNormal/normal` -> ``
- `/Login.img/RaceSelect/normal/BtNormal/mouseOver` -> ``
- `/Login.img/RaceSelect/normal/BtNormal/pressed` -> ``
- `/Login.img/RaceSelect/normal/BtNormal/disabled` -> ``
- `/Login.img/RaceSelect/normal/OnAnimation` -> ``
- `/Login.img/RaceSelect/normal/OffAnimation` -> ``
- `/Login.img/RaceSelect/aran` -> `text, BtAran, OnAnimation, OffAnimation`
- `/Login.img/RaceSelect/aran/text` -> ``
- `/Login.img/RaceSelect/aran/BtAran` -> `normal, mouseOver, pressed, disabled`
- `/Login.img/RaceSelect/aran/BtAran/normal` -> ``
- `/Login.img/RaceSelect/aran/BtAran/mouseOver` -> ``
- `/Login.img/RaceSelect/aran/BtAran/pressed` -> ``
- `/Login.img/RaceSelect/aran/BtAran/disabled` -> ``
- `/Login.img/RaceSelect/aran/OnAnimation` -> ``
- `/Login.img/RaceSelect/aran/OffAnimation` -> ``
- `/Login.img/RaceSelect/aran1` -> `text, BtAran, OnAnimation, OffAnimation`
- `/Login.img/RaceSelect/aran1/text` -> ``
- `/Login.img/RaceSelect/aran1/BtAran` -> `normal, mouseOver, pressed, disabled`
- `/Login.img/RaceSelect/aran1/BtAran/normal` -> ``
- `/Login.img/RaceSelect/aran1/BtAran/mouseOver` -> ``
- `/Login.img/RaceSelect/aran1/BtAran/pressed` -> ``
- `/Login.img/RaceSelect/aran1/BtAran/disabled` -> ``
- `/Login.img/RaceSelect/aran1/OnAnimation` -> ``
- `/Login.img/RaceSelect/aran1/OffAnimation` -> ``
- `/Login.img/RaceSelect/textGL` -> ``

## Creation image families
- NewChar: present
- NewCharKnight: present
- NewCharAran: present
- NewCharEvan: missing
- NewCharRes: missing

## Runtime routing anchors
- v83 CLogin::Update: 0x005F4C16
- race read: 0x005F4F26 (CLogin+0x214)
- case 0 Cygnus arm: 0x005F505E
- case 1 Explorer arm: 0x005F4FD0
- case 2 Aran arm: 0x005F4F42
- default for race >=3: 0x005F50E7
- SendNewCharPacket: 0x005F7E7A; v83 wire keeps one Encode4 race and no sub-job field.
