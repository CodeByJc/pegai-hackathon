class Engine:
    def calculate_efficiency(self, distance, fuel_used):
        # ZeroDivisionError if fuel_used is 0
        return distance / fuel_used
