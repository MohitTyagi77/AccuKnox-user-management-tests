
import requests
import logging
import datetime
import os

# ─── Configuration ────────────────────────────────────────────────────────────

# Add or remove URLs to monitor here
URLS_TO_CHECK = [
    "https://www.google.com",
    "https://httpbin.org/status/200",       # Always returns 200 (UP)
    "https://httpbin.org/status/500",       # Always returns 500 (DOWN)
    "https://httpbin.org/status/404",       # Always returns 404 (DOWN)
    "https://this-site-does-not-exist.xyz", # Unreachable (DOWN)
]

# HTTP status codes considered "healthy / UP"
HEALTHY_CODES = {200, 201, 202, 204, 301, 302}

TIMEOUT_SECONDS = 5   # Max wait time per request
LOG_FILE = "app_health.log"

# ─── Logger Setup ─────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  [%(levelname)s]  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(open(1, 'w', encoding='utf-8', closefd=False)),
    ]
)
logger = logging.getLogger(__name__)


# ─── Core Check ───────────────────────────────────────────────────────────────

def check_url(url: str) -> dict:
    """
    Performs an HTTP GET request to the given URL and determines
    whether the application is UP or DOWN.

    Returns a dict with:
        - url
        - status  : "UP" or "DOWN"
        - code    : HTTP status code (int) or None if unreachable
        - reason  : Short description (e.g. "OK", "Internal Server Error")
        - response_time_ms : Round-trip time in milliseconds or None
        - error   : Error message string if request failed, else None
    """
    result = {
        "url":              url,
        "status":           "DOWN",
        "code":             None,
        "reason":           None,
        "response_time_ms": None,
        "error":            None,
    }

    try:
        response = requests.get(url, timeout=TIMEOUT_SECONDS, allow_redirects=True)
        result["code"]             = response.status_code
        result["reason"]           = response.reason
        result["response_time_ms"] = round(response.elapsed.total_seconds() * 1000, 1)

        if response.status_code in HEALTHY_CODES:
            result["status"] = "UP"
        else:
            result["status"] = "DOWN"

    except requests.exceptions.ConnectionError as e:
        result["error"] = "Connection error — host unreachable or DNS failed"
    except requests.exceptions.Timeout:
        result["error"] = f"Request timed out after {TIMEOUT_SECONDS}s"
    except requests.exceptions.RequestException as e:
        result["error"] = str(e)

    return result


# ─── Report Printer ───────────────────────────────────────────────────────────

def _status_icon(status: str) -> str:
    return "🟢 UP  " if status == "UP" else "🔴 DOWN"


def log_result(result: dict) -> None:
    """Print and log a single URL result."""
    icon = _status_icon(result["status"])

    if result["code"] is not None:
        detail = (
            f"HTTP {result['code']} {result['reason']}  "
            f"| Response: {result['response_time_ms']} ms"
        )
    else:
        detail = f"Error: {result['error']}"

    logger.info(f"  {icon}  {result['url']}")
    logger.info(f"           └─ {detail}")


# ─── Main Runner ──────────────────────────────────────────────────────────────

def run_health_checks(urls: list = None) -> list:
    """
    Run health checks on all configured URLs and print a summary report.
    Returns list of result dicts.
    """
    if urls is None:
        urls = URLS_TO_CHECK

    separator = "=" * 65
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    logger.info(separator)
    logger.info(f"  APPLICATION HEALTH CHECK REPORT  —  {timestamp}")
    logger.info(separator)
    logger.info(f"  Checking {len(urls)} application(s)  |  Timeout: {TIMEOUT_SECONDS}s")
    logger.info(separator)

    results = []
    for url in urls:
        result = check_url(url)
        results.append(result)
        log_result(result)

    # ── Summary ──
    total   = len(results)
    up      = sum(1 for r in results if r["status"] == "UP")
    down    = total - up

    logger.info(separator)
    logger.info(f"  SUMMARY:  {up}/{total} applications UP  |  {down}/{total} DOWN")

    if down > 0:
        logger.warning(f"  ⚠️  {down} application(s) require attention!")
        for r in results:
            if r["status"] == "DOWN":
                logger.warning(f"      ❌  {r['url']}")

    logger.info(separator)
    logger.info(f"  Report saved to: {os.path.abspath(LOG_FILE)}")
    logger.info(separator)

    return results


# ─── Entry Point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    run_health_checks()
