import time
import psutil
import hashlib
from datetime import datetime

def capture_entropy_snapshot():
    """Captures a snapshot of system entropy."""
    snapshot = {
        'timestamp': datetime.utcnow().isoformat(),
        'keystroke_capture': time.time_ns() % 2**32,
        'cpu_jitter': psutil.cpu_percent(interval=0.1),
        'memory_free': psutil.virtual_memory().free,
        'boot_time': psutil.boot_time() % 65536,
        'process_count': len(psutil.pids()),
        'monotonic_ns': time.monotonic_ns() % 2**16
    }
    # Create a unique seed hash from the snapshot
    seed_string = ''.join(str(v) for v in snapshot.values())
    seed_hash = hashlib.sha256(seed_string.encode()).hexdigest()
    
    return snapshot, seed_hash

if __name__ == "__main__":
    data, seed = capture_entropy_snapshot()
    print(f"Entropy Snapshot: {data}")
    print(f"Unique Seed Hash: {seed}")