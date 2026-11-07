from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


def main() -> None:
    directory = str(Path(__file__).resolve().parent / "static")
    handler = partial(SimpleHTTPRequestHandler, directory=directory)
    server = ThreadingHTTPServer(("127.0.0.1", 9100), handler)
    print("Origin: http://127.0.0.1:9100")
    server.serve_forever()


if __name__ == "__main__":
    main()
