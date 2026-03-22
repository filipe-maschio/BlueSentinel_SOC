import os

# 📌 Diretório raiz do projeto
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 📁 Pastas principais
DATA_DIR = os.path.join(ROOT_DIR, "data")
CONFIG_DIR = os.path.join(ROOT_DIR, "config")
MODULES_DIR = os.path.join(ROOT_DIR, "modules")
EXTERNAL_DIR = os.path.join(ROOT_DIR, "external", "spiderfoot")

# 📄 Arquivos específicos
TARGETS_FILE = os.path.join(CONFIG_DIR, "targets_for_spiderfoot.txt")

# 🧠 SpiderFoot
SPIDERFOOT_PATH = os.path.join(EXTERNAL_DIR, "sf.py")

# 🔥 Ensure required directories exist
os.makedirs(DATA_DIR, exist_ok=True)