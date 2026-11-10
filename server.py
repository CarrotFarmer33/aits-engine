#!/usr/bin/env python3
"""server.py - Cloud API Backend for AITS Practice Portal Vector PDF Generator.

Deployable to Render, Railway, Fly.io, or any Docker container.
Crops vector questions and solutions directly from source PDFs using PyMuPDF.
"""

import http.server
import json
import mimetypes
import os
import sys
import threading
import time
import urllib.parse

from build_vector_test import build_test_pdf, QuestionManager

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
GENERATED_DIR = os.path.join(ROOT_DIR, "generated_tests")
os.makedirs(GENERATED_DIR, exist_ok=True)

# Pre-load question manager in background thread on startup
threading.Thread(target=QuestionManager.get_instance, daemon=True).start()

def cleanup_old_pdfs():
    """Periodically remove PDFs older than 1 hour to prevent disk growth."""
    while True:
        try:
            now = time.time()
            for fname in os.listdir(GENERATED_DIR):
                if fname.endswith(".pdf") and fname != "latest_test.pdf":
                    fpath = os.path.join(GENERATED_DIR, fname)
                    if os.path.isfile(fpath) and (now - os.path.getmtime(fpath) > 3600):
                        try:
                            os.remove(fpath)
                        except Exception:
                            pass
        except Exception:
            pass
        time.sleep(900)  # Sweep every 15 minutes

threading.Thread(target=cleanup_old_pdfs, daemon=True).start()

class AitsEngineHandler(http.server.BaseHTTPRequestHandler):
    def end_headers(self):
        # Enable full CORS for web portal
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization, Accept")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Content-Length", "0")
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path in ("/", "/api", "/health"):
            self.send_json({
                "ok": True,
                "service": "AITS Vector PDF Engine",
                "status": "online",
                "timestamp": int(time.time())
            })
            return

        if path == "/api/status":
            self.handle_status()
            return

        if path.startswith("/generated_tests/"):
            self.handle_serve_pdf(path)
            return

        self.send_json({"ok": False, "error": f"Endpoint '{path}' not found"}, 404)

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path in ("/api/build-test", "/api/build-sheet"):
            self.handle_build_test()
            return

        self.send_json({"ok": False, "error": f"Endpoint '{path}' not found"}, 404)

    def handle_status(self):
        qm = QuestionManager.get_instance()
        cached_count = len(qm.segments_cache.get("questions", {})) + len(qm.segments_cache.get("solutions", {}))
        payload = {
            "ok": True,
            "status": "ready",
            "totalQuestions": len(qm.questions),
            "questionPdfs": len(qm.pdfs),
            "solutionPdfs": len(qm.sol_files),
            "cachedSegments": cached_count,
            "engineVersion": "2.0-cached"
        }
        self.send_json(payload)

    def handle_serve_pdf(self, path):
        # Extract filename safely
        fname = os.path.basename(path)
        fpath = os.path.join(GENERATED_DIR, fname)
        if not os.path.isfile(fpath):
            self.send_json({"ok": False, "error": "PDF not found or expired"}, 404)
            return

        try:
            with open(fpath, "rb") as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-Type", "application/pdf")
            self.send_header("Content-Length", str(len(content)))
            self.send_header("Content-Disposition", f'inline; filename="{fname}"')
            self.end_headers()
            self.wfile.write(content)
        except Exception as e:
            self.send_json({"ok": False, "error": str(e)}, 500)

    def handle_build_test(self):
        content_len = int(self.headers.get("Content-Length", 0))
        if content_len == 0:
            self.send_json({"ok": False, "error": "Empty request body"}, 400)
            return

        body = self.rfile.read(content_len).decode("utf-8")
        try:
            req = json.loads(body)
        except Exception as e:
            self.send_json({"ok": False, "error": f"Invalid JSON: {e}"}, 400)
            return

        chapters = req.get("chapters", [])
        subjects = req.get("subjects", [])
        pattern = req.get("pattern", "adv")
        paper = req.get("paper", "all")
        num_subjs = len(subjects) if subjects else 3
        default_count = (num_subjs * 25) if pattern == "main" else 30
        count = int(req.get("count") or default_count)
        title = req.get("title", "JEE ADVANCED PRACTICE TEST")
        subtitle = req.get("subtitle", "Chapter-wise Practice Sheet | Questions cropped from source papers")
        include_sol = bool(req.get("includeSolutions", True))
        remove_wm = bool(req.get("removeWatermark", True))
        selected_qids = req.get("qids", None)

        ts = int(time.time() * 1000)
        out_filename = f"test_{ts}.pdf"
        out_pdf = os.path.join(GENERATED_DIR, out_filename)

        try:
            t0 = time.time()
            res = build_test_pdf(
                chapters=chapters,
                subjects=subjects,
                count=count,
                pattern=pattern,
                paper=paper,
                title=title,
                subtitle=subtitle,
                include_solutions=include_sol,
                remove_watermark=remove_wm,
                selected_qids=selected_qids,
                out_pdf=out_pdf,
                shuffle=True
            )
            duration = round(time.time() - t0, 2)

            pdf_url = f"/generated_tests/{out_filename}"
            latest_url = "/generated_tests/latest_test.pdf"

            self.send_json({
                "ok": True,
                "pdfUrl": pdf_url,
                "latestUrl": latest_url,
                "filename": out_filename,
                "totalQuestions": res["total_questions"],
                "totalPages": res["total_pages"],
                "answerCount": res["answer_count"],
                "durationSeconds": duration
            })
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.send_json({"ok": False, "error": str(e)}, 500)

    def send_json(self, data, status_code=200):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

def run(port=8000):
    mimetypes.add_type("application/pdf", ".pdf")
    mimetypes.add_type("application/json", ".json")

    server_address = ("", port)
    httpd = http.server.ThreadingHTTPServer(server_address, AitsEngineHandler)
    print(f"AITS Vector PDF Engine running on port {port}")
    print(f"Generated PDFs stored in: {GENERATED_DIR}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        httpd.server_close()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", sys.argv[1] if len(sys.argv) > 1 else 8000))
    run(port)
