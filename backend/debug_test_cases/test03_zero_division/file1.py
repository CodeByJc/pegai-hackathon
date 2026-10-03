from file2 import Engine
from file3 import read_sensor_data

def control_loop():
    data = read_sensor_data()
    engine = Engine()
    efficiency = engine.calculate_efficiency(data['distance'], data['fuel_used'])
    print("Efficiency:", efficiency)

if __name__ == '__main__':
    control_loop()
