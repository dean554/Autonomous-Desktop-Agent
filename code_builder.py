from pathlib import Path

SANDBOX = "sandbox"

class StagedCodeBuilder:
    def __init__(self, file_name, code):
        self.file_name = file_name
        self.code = code
        self.file_path = ""

    def create_file(self):
        self.file_path = Path(f"{SANDBOX}/{self.file_name}")
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

    def append_code(self):
        self.file_path.write_text(self.code)

    def execute(self):
        self.create_file()
        self.append_code()

