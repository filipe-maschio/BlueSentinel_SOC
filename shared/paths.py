import os

# Project root directory
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Main directories
DATA_DIR = os.path.join(ROOT_DIR, "data")
CONFIG_DIR = os.path.join(ROOT_DIR, "config")
MODULES_DIR = os.path.join(ROOT_DIR, "modules")
EXTERNAL_DIR = os.path.join(ROOT_DIR, "external", "spiderfoot")
LOGS_DIR = os.path.join(ROOT_DIR, "logs")

# Configuration files
TARGETS_FILE = os.path.join(CONFIG_DIR, "targets_for_spiderfoot.txt")

# SpiderFoot
SPIDERFOOT_PATH = os.path.join(EXTERNAL_DIR, "sf.py")

# Pipeline directories
PIPELINE_RUNS_DIR = os.path.join(DATA_DIR, "pipeline_runs")

# SpiderFoot outputs
SPIDERFOOT_OUTPUTS_DIR = os.path.join(DATA_DIR, "spiderfoot_outputs")

# Detection files
ALERT_HISTORY_FILE = os.path.join(DATA_DIR, "alert_history.log")
ALERT_HISTORY_LOCK_FILE = ALERT_HISTORY_FILE + ".lock"

# Ensure required directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(PIPELINE_RUNS_DIR, exist_ok=True)
os.makedirs(SPIDERFOOT_OUTPUTS_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)