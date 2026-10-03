def parse_csv_line(line):
    parts = line.split(',')
    # Bug: assumes there are always 3 elements
    return {
        "id": parts[0],
        "name": parts[1],
        "role": parts[2]
    }
