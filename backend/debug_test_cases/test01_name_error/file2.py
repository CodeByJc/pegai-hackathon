def calculate_metrics(data):
    # Bug: 'mean' is not imported or defined
    avg = mean(data)
    return {"average": avg, "count": len(data)}
