import hashlib

#Network params
HOST = "127.0.0.1"
PORT = 9999

#Auth
SECRET = "5ce9d0261f3fb421a883026d15c2b41e8d817cf2e3fd15bd9ba2a8998a6b3c49"
SECRET_HASH = hashlib.sha256(SECRET.encode()).hexdigest()

#Pipeline
WINDOW_SIZE = 10 # number of readings in the sliding window for z-score 
ZSCORE_THRESHOLD = 3 # stds to flag a statistical anomaly

# Physical limits, enforced by Validator
# Values outside these ranges are physically impossible
PHYSICAL_LIMITS = {
    "cpu":     (0.0, 100.0),
    "ram":     (0.0, 100.0),
    "disk":    (0.0, 100.0),
    "network": (0.0, float("inf")),
}

# Alert thresholds, enforced by ThresholdDetector
# Values outside these ranges are possible but considered abnormal
# Configured to be tweakable
ALERT_THRESHOLDS = {
    "cpu":     (0.0, 90.0),
    "ram":     (0.0, 85.0),
    "disk":    (0.0, 80.0),
    "network": (0.0, float("inf")),
}