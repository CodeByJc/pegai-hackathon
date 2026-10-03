from file2 import parse_csv_line
from file3 import get_raw_lines

def extract_users():
    lines = get_raw_lines()
    users = []
    for line in lines:
        users.append(parse_csv_line(line))
    return users

if __name__ == '__main__':
    print(extract_users())
