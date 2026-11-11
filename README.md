---
title: AITS Vector Engine
emoji: ⚡
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
pinned: false
---

# AITS Vector PDF Engine

Cloud-hosted backend for the **AITS Practice Portal** test builder.
Generates 100% native vector test PDFs on-the-fly directly cropped from official JEE source papers with zero rasterization and crisp selectable text.

## Features
- **Native Vector Cropping**: Mathematical equations, chemical structures, and vector diagrams remain pin-sharp at any zoom level.
- **Watermark Removal**: Strips header banners, FIITJEE watermarks, and footers automatically.
- **Pattern Support**: Full JEE Main (Section A + Section B) and JEE Advanced patterns.
- **Worked Solutions & Answer Key**: Appends matched worked solutions and an answer key grid to each sheet.
- **CORS Enabled**: Ready to serve frontend requests from Vercel, GitHub Pages, or localhost.

## Local Development
```bash
pip install -r requirements.txt
python server.py 7860
```
