from file2 import init_db
from file3 import load_env

def start_server():
    env = load_env()
    db = init_db(env)
    print("DB initialized")

if __name__ == '__main__':
    start_server()
