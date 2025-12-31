import os

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