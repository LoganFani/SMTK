import os
import sys
from pathlib import Path

class TempDirHandler:
    def __init__(self, dir_name = ".tmp"):
        self.dir_name = dir_name
        self._create_temp_dir()

    def _create_temp_dir(self) -> bool:
        if not os.path.exists(self.dir_name):
            os.makedirs(self.dir_name)
            return True
        return False
    
    def delete_temp_dir(self) -> None:
        if os.path.exists(self.dir_name):
            for filename in os.listdir(self.dir_name):
                file_path = os.path.join(self.dir_name, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)
            os.rmdir(self.dir_name)

    
# ONE DIR PYINSTALLER
def is_frozen() -> bool:
    return getattr(sys, "frozen", False)


def app_root() -> Path:
    """
    Root directory for bundled app resources.
    - dev: project root
    - onedir: SMTK.app/Contents/MacOS
    - onefile: _MEIPASS (temp extract dir)
    """
    if is_frozen():
        return Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent))
    return Path(__file__).resolve().parent.parent


# For read only resources
def resource_path(*relative: str) -> Path:
    """
    Read-only bundled resources (templates, static, media, db).
    """
    return app_root().joinpath(*relative)


# For DB
def db_path(name: str = "decks.db") -> Path:
    return resource_path(name)

def exe_dir() -> Path:
    """Return the folder where the executable lives (or script in dev)."""
    if getattr(sys, "frozen", False):
        # Onedir / onefile: location of the binary
        return Path(sys.executable).parent
    # Dev mode
    return Path(__file__).resolve().parent
