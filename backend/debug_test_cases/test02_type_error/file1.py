from file2 import ProcessManager
from file3 import load_config

def run_system():
    config = load_config()
    manager = ProcessManager(config['timeout'])
    manager.start()

if __name__ == '__main__':
    run_system()
