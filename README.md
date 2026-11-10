# AITS Vector PDF Engine

Cloud-hosted backend for the **AITS Practice Portal** test builder.
Generates 100% native vector test PDFs on-the-fly directly cropped from official JEE source papers with zero rasterization and crisp selectable text.

## Features
- **Native Vector Cropping**: Mathematical equations, chemical structures, and vector diagrams remain pin-sharp at any zoom level.
- **Watermark Removal**: Strips header banners, FIITJEE watermarks, and footers automatically.
- **Pattern Support**: Full JEE Main (Section A + Section B) and JEE Advanced patterns.
- **Worked Solutions & Answer Key**: Appends matched worked solutions and an answer key grid to each sheet.
- **CORS Enabled**: Ready to serve frontend requests from Vercel or localhost.

## Deploying to Render
1. Log in to [Render.com](https://render.com) using your GitHub account.
2. Click **New +** -> **Web Service**.
3. Connect repository `CarrotFarmer33/aits-engine`.
4. Render automatically detects the `Dockerfile` and builds the service.
5. Copy your Render URL (e.g., `https://aits-engine.onrender.com`) and paste it into `config.js` in your frontend portal repository.

## Local Development
```bash
pip install -r requirements.txt
python server.py 8000
```
