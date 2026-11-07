from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


class CDNHandler(SimpleHTTPRequestHandler):
    def end_headers(self) -> None:
        self.send_header("Cache-Control", "public, max-age=120")
        self.send_header("X-Cache-Mode", "local-cdn")
        super().end_headers()


def main() -> None:
    directory = str(Path(__file__).resolve().parent / "static")
    handler = partial(CDNHandler, directory=directory)
    server = ThreadingHTTPServer(("127.0.0.1", 9101), handler)
    print("CDN: http://127.0.0.1:9101")
    server.serve_forever()


if __name__ == "__main__":
    main()
