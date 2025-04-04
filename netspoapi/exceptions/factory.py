class APIErrorFactory(Exception):
    def __init__(self, code: int = None, name: str = None):
        self.code = int(code) if code else None
        self.name = name
        super().__init__(code)

    def __str__(self):
        return f"[{self.code}] {self.name}\n"
