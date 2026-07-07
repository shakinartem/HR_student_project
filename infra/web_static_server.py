from __future__ import annotations

import os
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


DIST_DIR = Path("/srv/web/dist")
HOST = "0.0.0.0"
PORT = int(os.environ.get("PORT", "8080"))


class SpaStaticHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIST_DIR), **kwargs)

    def do_GET(self) -> None:
        if self.path == "/health":
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"ok")
            return
        return super().do_GET()

    def send_head(self):
        path = self.translate_path(self.path)
        if os.path.isdir(path):
            for index in ("index.html",):
                index_path = os.path.join(path, index)
                if os.path.exists(index_path):
                    path = index_path
                    break
        if os.path.exists(path):
            return super().send_head()

        self.path = "/index.html"
        return super().send_head()


def main() -> None:
    server = ThreadingHTTPServer((HOST, PORT), SpaStaticHandler)
    server.serve_forever()


if __name__ == "__main__":
    main()
