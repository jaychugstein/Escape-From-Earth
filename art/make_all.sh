#!/bin/bash
# Rebuilds every picture and the course from these scripts, then packs the FX data and fxdata.h
# into ../EscapeFromEarth. Needs python3 with numpy, scipy and Pillow.
set -e
cd "$(dirname "$0")"
mkdir -p preview
python3 title_anim.py
python3 glorb.py
python3 glorb_happy.py
python3 controls.py
python3 menu_art.py
python3 scorebg.py
python3 mother.py
python3 ufo_rot.py
python3 level/gen_level.py
python3 fxpack.py
