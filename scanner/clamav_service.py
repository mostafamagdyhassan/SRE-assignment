import subprocess
from metrics import scan_duration_seconds, scan_failures_total
import time

def scan_file(path: str) -> str:
    start = time.time()
    try:
        result = subprocess.run(
            ["clamdscan", path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=120
        )

        duration = time.time() - start
        scan_duration_seconds.observe(duration)

        if result.returncode == 0:
            return "OK"
        elif result.returncode == 1:
            return "INFECTED"
        else:
            scan_failures_total.inc()
            raise Exception("ClamAV error")

    except Exception:
        scan_failures_total.inc()
        raise
