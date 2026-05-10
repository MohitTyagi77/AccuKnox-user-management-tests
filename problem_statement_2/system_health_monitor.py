

import psutil
import logging
import datetime
import os

# ─── Configuration ────────────────────────────────────────────────────────────

THRESHOLDS = {
    "cpu_percent":    80.0,   # Alert if CPU usage > 80%
    "memory_percent": 80.0,   # Alert if RAM usage > 80%
    "disk_percent":   85.0,   # Alert if Disk usage > 85%
    "top_processes":   5,     # How many top processes to display
}

LOG_FILE = "system_health.log"

# ─── Logger Setup ─────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  [%(levelname)s]  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),      # Write to log file
        logging.StreamHandler(),            # Also print to console
    ]
)
logger = logging.getLogger(__name__)


# ─── Helper ───────────────────────────────────────────────────────────────────

def alert(message: str) -> None:
    """Log an ALERT-level message (uses WARNING so it stands out)."""
    logger.warning("🚨 ALERT — " + message)


def ok(message: str) -> None:
    """Log an OK-level message."""
    logger.info("✅ OK     — " + message)


# ─── Check Functions ──────────────────────────────────────────────────────────

def check_cpu() -> dict:
    """Return CPU usage % (averaged over 1-second interval)."""
    usage = psutil.cpu_percent(interval=1)
    core_count = psutil.cpu_count(logical=True)
    result = {"usage_percent": usage, "core_count": core_count}

    if usage > THRESHOLDS["cpu_percent"]:
        alert(f"CPU usage is HIGH: {usage:.1f}%  (threshold: {THRESHOLDS['cpu_percent']}%)")
    else:
        ok(f"CPU usage: {usage:.1f}%  (cores: {core_count})")

    return result


def check_memory() -> dict:
    """Return RAM usage details."""
    mem = psutil.virtual_memory()
    result = {
        "total_gb":   round(mem.total / (1024 ** 3), 2),
        "used_gb":    round(mem.used  / (1024 ** 3), 2),
        "free_gb":    round(mem.available / (1024 ** 3), 2),
        "usage_percent": mem.percent,
    }

    if mem.percent > THRESHOLDS["memory_percent"]:
        alert(
            f"Memory usage is HIGH: {mem.percent:.1f}%  "
            f"({result['used_gb']} GB used of {result['total_gb']} GB)"
        )
    else:
        ok(
            f"Memory usage: {mem.percent:.1f}%  "
            f"({result['used_gb']} GB used / {result['total_gb']} GB total)"
        )

    return result


def check_disk(path: str = "/") -> dict:
    """Return disk usage for a given mount path."""
    disk = psutil.disk_usage(path)
    result = {
        "path":          path,
        "total_gb":      round(disk.total / (1024 ** 3), 2),
        "used_gb":       round(disk.used  / (1024 ** 3), 2),
        "free_gb":       round(disk.free  / (1024 ** 3), 2),
        "usage_percent": disk.percent,
    }

    if disk.percent > THRESHOLDS["disk_percent"]:
        alert(
            f"Disk usage is HIGH on '{path}': {disk.percent:.1f}%  "
            f"({result['used_gb']} GB used of {result['total_gb']} GB)"
        )
    else:
        ok(
            f"Disk usage on '{path}': {disk.percent:.1f}%  "
            f"({result['free_gb']} GB free of {result['total_gb']} GB)"
        )

    return result


def check_processes(top_n: int = 5) -> list:
    """Return top N processes sorted by CPU usage."""
    procs = []
    for p in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent", "status"]):
        try:
            procs.append(p.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    # Sort by CPU usage descending
    procs.sort(key=lambda x: x.get("cpu_percent") or 0, reverse=True)
    top = procs[:top_n]

    logger.info(f"📋 Top {top_n} processes by CPU usage:")
    logger.info(f"  {'PID':>6}  {'CPU%':>6}  {'MEM%':>6}  {'STATUS':<10}  NAME")
    logger.info(f"  {'─'*6}  {'─'*6}  {'─'*6}  {'─'*10}  {'─'*20}")
    for p in top:
        logger.info(
            f"  {p['pid']:>6}  "
            f"{(p['cpu_percent'] or 0):>5.1f}%  "
            f"{(p['memory_percent'] or 0):>5.1f}%  "
            f"{(p['status'] or 'N/A'):<10}  "
            f"{p['name']}"
        )

    return top


# ─── Main Report ──────────────────────────────────────────────────────────────

def run_health_check() -> None:
    """Run all health checks and produce a full report."""
    separator = "=" * 60
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    logger.info(separator)
    logger.info(f"  SYSTEM HEALTH REPORT  —  {timestamp}")
    logger.info(separator)

    cpu_data    = check_cpu()
    mem_data    = check_memory()
    disk_data   = check_disk("/")
    proc_data   = check_processes(top_n=THRESHOLDS["top_processes"])

    logger.info(separator)
    logger.info(f"  Report saved to: {os.path.abspath(LOG_FILE)}")
    logger.info(separator)

    return {
        "cpu":       cpu_data,
        "memory":    mem_data,
        "disk":      disk_data,
        "processes": proc_data,
    }


# ─── Entry Point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    run_health_check()
