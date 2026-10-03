from file2 import get_feature_flags
from file3 import process_data

def main():
    flags = get_feature_flags()
    process_data(flags)

if __name__ == '__main__':
    main()
