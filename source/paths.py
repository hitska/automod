from os.path import dirname, abspath
from pathlib import Path


class Paths:
    def __init__(self):
        self.dirname_source = Path(dirname(abspath(__file__)))
        self.dirname_root = self.dirname_source.parent
        self.dirname_docker_image = self.dirname_root / "docker"
        self.tmp_dir =  self.dirname_root / "tmp"

        self.filename_settings = self.dirname_root / "settings.json"
        self.filename_log = self.dirname_root / "log.txt"

paths = Paths()
