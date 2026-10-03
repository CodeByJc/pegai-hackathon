from file2 import calculate_metrics
from file3 import get_data

def main():
    data = get_data()
    metrics = calculate_metrics(data)
    print("Metrics:", metrics)

if __name__ == '__main__':
    main()
