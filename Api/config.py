import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent


MEDIA_ROOT = os.path.join(BASE_DIR, "src/media")