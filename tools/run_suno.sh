#!/bin/bash
export DISPLAY=:10
export XAUTHORITY=/home/nova/.Xauthority
cd /mnt/coding/projects/personal/songs-gen
.env-song-gens/bin/python -u tools/suno_worker.py --interval 30
