import time

class ProcessManager:
    def __init__(self, timeout_ms):
        self.timeout_ms = timeout_ms

    def start(self):
        # TypeError: unsupported operand type(s) for /: 'str' and 'int'
        timeout_sec = self.timeout_ms / 1000
        time.sleep(timeout_sec)
