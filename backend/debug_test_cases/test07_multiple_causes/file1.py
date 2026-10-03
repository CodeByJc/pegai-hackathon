from file2 import fetch_user
from file3 import render_profile

def display_user(user_id):
    user = fetch_user(user_id)
    print(render_profile(user))

if __name__ == '__main__':
    display_user(42)
