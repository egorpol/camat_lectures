"""Serve only the workshop's transfer MEI and page resources on loopback, with CORS.

python tools/serve_mei_friend_preview.py /path/to/schumann_edition_work/edition --port 8781
Stop with Ctrl+C after the rehearsal. Never point this server at private files.
"""
import argparse
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    parser.add_argument("--port", type=int, default=8781)
    args = parser.parse_args()
    root = args.root.resolve()
    allowed = {"/mei/work.mei", "/mei/mei-friend-transfer.mei", "/pages/pages.json"}
    allowed.update("/pages/" + path.name for path in (root / "pages").glob("page-*.png"))
    class Handler(SimpleHTTPRequestHandler):
        def __init__(self, *params, **kwargs):
            super().__init__(*params, directory=str(root), **kwargs)
        def end_headers(self):
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET, HEAD, OPTIONS")
            self.send_header("Access-Control-Allow-Private-Network", "true")
            super().end_headers()
        def do_GET(self):
            if unquote(urlsplit(self.path).path) not in allowed:
                self.send_error(404)
                return
            super().do_GET()
        def do_HEAD(self):
            if unquote(urlsplit(self.path).path) not in allowed:
                self.send_error(404)
                return
            super().do_HEAD()
        def do_OPTIONS(self):
            self.send_response(204)
            self.end_headers()
    print(f"Serving transfer files only at http://127.0.0.1:{args.port}/", flush=True)
    ThreadingHTTPServer(("127.0.0.1", args.port), Handler).serve_forever()


if __name__ == "__main__":
    main()
