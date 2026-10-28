import argparse
from functools import partial
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit


DEFAULT_PAGE = Path(
    r"C:\Users\user\.copilot\attachments"
    r"\pasted-text-6b1f3587-267d-45d9-aba4-293de0e37f6b.txt"
)


class WeatherAppHandler(BaseHTTPRequestHandler):
    page_path: Path

    def do_GET(self):
        if urlsplit(self.path).path not in ("/", "/index.html"):
            self.send_error(404, "Not found")
            return

        self._send_page(include_body=True)

    def do_HEAD(self):
        if urlsplit(self.path).path not in ("/", "/index.html"):
            self.send_error(404, "Not found")
            return

        self._send_page(include_body=False)

    def _send_page(self, include_body: bool):
        try:
            page = self.page_path.read_bytes()
        except OSError:
            self.send_error(500, "Unable to read the HTML page")
            return

        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(page)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()

        if include_body:
            self.wfile.write(page)

    def log_message(self, format_string: str, *args):
        print(f"{self.address_string()} - {format_string % args}")


def main():
    parser = argparse.ArgumentParser(
        description="Serve the Skyline weather app locally."
    )
    parser.add_argument(
        "--page",
        type=Path,
        default=DEFAULT_PAGE,
        help="Path to the attached HTML text file.",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Local port to serve on (default: 8000).",
    )
    args = parser.parse_args()

    if not args.page.is_file():
        parser.error(f"HTML page not found: {args.page}")

    handler = type(
    "ConfiguredWeatherAppHandler",
    (WeatherAppHandler,),
    {"page_path": args.page},
)

    address = ("127.0.0.1", args.port)
    try:
        with ThreadingHTTPServer(address, handler) as server:
            print(f"Serving the weather app at http://127.0.0.1:{args.port}/")
            print("Press Ctrl+C to stop.")
            server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
    except OSError as error:
        parser.error(f"Could not start the local server: {error}")


if __name__ == "__main__":
    main()