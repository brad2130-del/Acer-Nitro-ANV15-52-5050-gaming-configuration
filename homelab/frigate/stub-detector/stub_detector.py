#!/usr/bin/env python3
"""DeepStack-compatible stub detector for testing Frigate before the Pixel endpoint exists.

Frigate POSTs a multipart JPEG to /v1/vision/detection and expects:
    {"success": true, "predictions": [{"label", "confidence",
                                       "x_min", "y_min", "x_max", "y_max"}, ...]}

This stub returns no detections (or one fake person with --fake-person) so you can
verify the whole pipeline end to end. The Pixel app must serve the same contract.

    python3 stub_detector.py --port 8080 [--fake-person]
"""
import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

FAKE_PERSON = False


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path.rstrip("/") != "/v1/vision/detection":
            self.send_error(404)
            return
        length = int(self.headers.get("Content-Length", 0))
        self.rfile.read(length)  # discard the image
        predictions = []
        if FAKE_PERSON:
            predictions.append({"label": "person", "confidence": 0.9,
                                "x_min": 100, "y_min": 50, "x_max": 200, "y_max": 300})
        body = json.dumps({"success": True, "predictions": predictions}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        pass


def main():
    global FAKE_PERSON
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--fake-person", action="store_true",
                        help="always report one person, to test alerts/recording")
    args = parser.parse_args()
    FAKE_PERSON = args.fake_person
    print(f"stub detector on http://{args.host}:{args.port}/v1/vision/detection")
    ThreadingHTTPServer((args.host, args.port), Handler).serve_forever()


if __name__ == "__main__":
    main()
