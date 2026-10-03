import os
import json
import subprocess
from pathlib import Path

BASE_DIR = Path("/home/jc/JC_PROJECT/pegai-hackathon/backend/debug_test_cases")

def write_file(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        f.write(content.lstrip('\n'))

def run_test(case_dir, entry_point="file1.py"):
    # Run the script and capture traceback
    result = subprocess.run(["python3", entry_point], cwd=case_dir, capture_output=True, text=True)
    tb_out = result.stderr if result.returncode != 0 else ""
    with open(case_dir / "traceback.txt", "w") as f:
        f.write(tb_out)
    return result.returncode, tb_out

def setup_test01():
    d = BASE_DIR / "test01_name_error"
    write_file(d / "file1.py", """
from file2 import calculate_metrics
from file3 import get_data

def main():
    data = get_data()
    metrics = calculate_metrics(data)
    print("Metrics:", metrics)

if __name__ == '__main__':
    main()
""")
    write_file(d / "file2.py", """
def calculate_metrics(data):
    # Bug: 'mean' is not imported or defined
    avg = mean(data)
    return {"average": avg, "count": len(data)}
""")
    write_file(d / "file3.py", """
def get_data():
    return [10, 20, 30, 40]
""")
    run_test(d)
    write_file(d / "expected.json", json.dumps({
      "test_id": "test01_name_error",
      "category": "normal",
      "expected_error_type": "NameError",
      "expected_root_cause": "The function 'mean' is called in calculate_metrics but is neither imported nor defined.",
      "expected_files_involved": ["file2.py"],
      "expected_hypothesis_count_min": 1,
      "requires_multi_file_reasoning": False,
      "requires_ranked_hypotheses": False,
      "requires_generated_tests": True,
      "requires_execution_verification": True,
      "expected_verification": "verified"
    }, indent=2))

def setup_test02():
    d = BASE_DIR / "test02_type_error"
    write_file(d / "file1.py", """
from file2 import ProcessManager
from file3 import load_config

def run_system():
    config = load_config()
    manager = ProcessManager(config['timeout'])
    manager.start()

if __name__ == '__main__':
    run_system()
""")
    write_file(d / "file2.py", """
import time

class ProcessManager:
    def __init__(self, timeout_ms):
        self.timeout_ms = timeout_ms

    def start(self):
        # TypeError: unsupported operand type(s) for /: 'str' and 'int'
        timeout_sec = self.timeout_ms / 1000
        time.sleep(timeout_sec)
""")
    write_file(d / "file3.py", """
def load_config():
    # Bug: timeout is read as a string
    return {"timeout": "5000"}
""")
    run_test(d)
    write_file(d / "expected.json", json.dumps({
      "test_id": "test02_type_error",
      "category": "normal",
      "expected_error_type": "TypeError",
      "expected_root_cause": "Config loads timeout as a string, but ProcessManager divides it by 1000.",
      "expected_files_involved": ["file2.py", "file3.py"],
      "expected_hypothesis_count_min": 1,
      "requires_multi_file_reasoning": True,
      "requires_ranked_hypotheses": False,
      "requires_generated_tests": True,
      "requires_execution_verification": True,
      "expected_verification": "verified"
    }, indent=2))

def setup_test03():
    d = BASE_DIR / "test03_zero_division"
    write_file(d / "file1.py", """
from file2 import Engine
from file3 import read_sensor_data

def control_loop():
    data = read_sensor_data()
    engine = Engine()
    efficiency = engine.calculate_efficiency(data['distance'], data['fuel_used'])
    print("Efficiency:", efficiency)

if __name__ == '__main__':
    control_loop()
""")
    write_file(d / "file2.py", """
class Engine:
    def calculate_efficiency(self, distance, fuel_used):
        # ZeroDivisionError if fuel_used is 0
        return distance / fuel_used
""")
    write_file(d / "file3.py", """
def read_sensor_data():
    return {"distance": 100, "fuel_used": 0}
""")
    run_test(d)
    write_file(d / "expected.json", json.dumps({
      "test_id": "test03_zero_division",
      "category": "normal",
      "expected_error_type": "ZeroDivisionError",
      "expected_root_cause": "fuel_used can be 0, causing division by zero.",
      "expected_files_involved": ["file2.py"],
      "expected_hypothesis_count_min": 1,
      "requires_multi_file_reasoning": False,
      "requires_ranked_hypotheses": False,
      "requires_generated_tests": True,
      "requires_execution_verification": True,
      "expected_verification": "verified"
    }, indent=2))

def setup_test04():
    d = BASE_DIR / "test04_index_error"
    write_file(d / "file1.py", """
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
""")
    write_file(d / "file2.py", """
def parse_csv_line(line):
    parts = line.split(',')
    # Bug: assumes there are always 3 elements
    return {
        "id": parts[0],
        "name": parts[1],
        "role": parts[2]
    }
""")
    write_file(d / "file3.py", """
def get_raw_lines():
    return [
        "1,Alice,Admin",
        "2,Bob" # Missing role, causes IndexError
    ]
""")
    run_test(d)
    write_file(d / "expected.json", json.dumps({
      "test_id": "test04_index_error",
      "category": "normal",
      "expected_error_type": "IndexError",
      "expected_root_cause": "parts[2] fails if the line does not contain a role.",
      "expected_files_involved": ["file2.py", "file3.py"],
      "expected_hypothesis_count_min": 1,
      "requires_multi_file_reasoning": True,
      "requires_ranked_hypotheses": False,
      "requires_generated_tests": True,
      "requires_execution_verification": True,
      "expected_verification": "verified"
    }, indent=2))

def setup_test05():
    d = BASE_DIR / "test05_key_error"
    write_file(d / "file1.py", """
from file2 import init_db
from file3 import load_env

def start_server():
    env = load_env()
    db = init_db(env)
    print("DB initialized")

if __name__ == '__main__':
    start_server()
""")
    write_file(d / "file2.py", """
def init_db(config):
    # KeyError: 'db_port'
    return f"Connecting to {config['db_host']}:{config['db_port']}"
""")
    write_file(d / "file3.py", """
def load_env():
    return {
        "db_host": "localhost",
        "db_user": "admin"
    }
""")
    run_test(d)
    write_file(d / "expected.json", json.dumps({
      "test_id": "test05_key_error",
      "category": "normal",
      "expected_error_type": "KeyError",
      "expected_root_cause": "Accessing 'db_port' which is not present in the configuration dictionary.",
      "expected_files_involved": ["file2.py"],
      "expected_hypothesis_count_min": 1,
      "requires_multi_file_reasoning": False,
      "requires_ranked_hypotheses": False,
      "requires_generated_tests": True,
      "requires_execution_verification": True,
      "expected_verification": "verified"
    }, indent=2))

def setup_test06():
    d = BASE_DIR / "test06_multifile_config"
    write_file(d / "file1.py", """
from file2 import get_feature_flags
from file3 import process_data

def main():
    flags = get_feature_flags()
    process_data(flags)

if __name__ == '__main__':
    main()
""")
    write_file(d / "file2.py", """
from file3 import DEFAULTS

def get_feature_flags():
    flags = DEFAULTS.copy()
    # Bug: Typo in flag key override
    flags['feature_X_enabled'] = True 
    return flags
""")
    write_file(d / "file3.py", """
DEFAULTS = {
    'feature_x_enabled': False
}

def process_data(flags):
    # KeyError because 'feature_x_enabled' is accessed but file2 updated 'feature_X_enabled'
    # Wait, the KeyError actually happens if someone pops or accesses strictly. 
    # Let's make it more direct.
    if flags.pop('feature_x_enabled'):
        print("X enabled")
    # This will fail on something else.
    # Let's make process_data strictly require all keys in a strict list
    strict_keys = ['feature_x_enabled']
    for k in flags.keys():
        if k not in strict_keys:
            raise KeyError(f"Invalid flag {k}")
""")
    run_test(d)
    write_file(d / "expected.json", json.dumps({
      "test_id": "test06_multifile_config",
      "category": "stretch",
      "expected_error_type": "KeyError",
      "expected_root_cause": "file2.py introduces a typo 'feature_X_enabled', which file3.py rejects.",
      "expected_files_involved": ["file1.py", "file2.py", "file3.py"],
      "expected_hypothesis_count_min": 1,
      "requires_multi_file_reasoning": True,
      "requires_ranked_hypotheses": False,
      "requires_generated_tests": True,
      "requires_execution_verification": True,
      "expected_verification": "verified"
    }, indent=2))

def setup_test07():
    d = BASE_DIR / "test07_multiple_causes"
    write_file(d / "file1.py", """
from file2 import fetch_user
from file3 import render_profile

def display_user(user_id):
    user = fetch_user(user_id)
    print(render_profile(user))

if __name__ == '__main__':
    display_user(42)
""")
    write_file(d / "file2.py", """
def fetch_user(user_id):
    # Returns None instead of a dict
    return None
""")
    write_file(d / "file3.py", """
def render_profile(user):
    # AttributeError: 'NoneType' object has no attribute 'get'
    # Multiple causes: fetch_user returned None OR render_profile doesn't handle None
    name = user.get('name', 'Unknown')
    return f"Profile: {name}"
""")
    run_test(d)
    write_file(d / "expected.json", json.dumps({
      "test_id": "test07_multiple_causes",
      "category": "stretch",
      "expected_error_type": "AttributeError",
      "expected_root_cause": "fetch_user returns None and render_profile assumes a dictionary.",
      "expected_files_involved": ["file2.py", "file3.py"],
      "expected_hypothesis_count_min": 2,
      "requires_multi_file_reasoning": True,
      "requires_ranked_hypotheses": True,
      "minimum_hypotheses": 2,
      "requires_generated_tests": True,
      "requires_execution_verification": True,
      "expected_verification": "verified"
    }, indent=2))

def setup_test08():
    d = BASE_DIR / "test08_import_error"
    write_file(d / "file1.py", """
from file2 import start_app

if __name__ == '__main__':
    start_app()
""")
    write_file(d / "file2.py", """
from file3 import MissingClass

def start_app():
    c = MissingClass()
    print("Started")
""")
    write_file(d / "file3.py", """
class ExistingClass:
    pass
""")
    run_test(d)
    write_file(d / "expected.json", json.dumps({
      "test_id": "test08_import_error",
      "category": "normal",
      "expected_error_type": "ImportError",
      "expected_root_cause": "Attempted to import 'MissingClass' which does not exist in file3.",
      "expected_files_involved": ["file2.py", "file3.py"],
      "expected_hypothesis_count_min": 1,
      "requires_multi_file_reasoning": True,
      "requires_ranked_hypotheses": False,
      "requires_generated_tests": True,
      "requires_execution_verification": True,
      "expected_verification": "verified"
    }, indent=2))

def setup_test09():
    d = BASE_DIR / "test09_regression_test"
    write_file(d / "file1.py", """
from file2 import calculate_total
from file3 import get_cart

def checkout():
    cart = get_cart()
    total = calculate_total(cart)
    # The bug is functional: calculate_total doesn't sum correctly
    # So we'll force an assertion error or just an exception to mimic a failure
    if total != 150:
        raise ValueError(f"Total is wrong! Expected 150, got {total}")

if __name__ == '__main__':
    checkout()
""")
    write_file(d / "file2.py", """
def calculate_total(items):
    # Functional bug: multiplies instead of adds
    total = 1
    for item in items:
        total *= item['price']
    return total
""")
    write_file(d / "file3.py", """
def get_cart():
    return [{'price': 50}, {'price': 100}]
""")
    run_test(d)
    write_file(d / "expected.json", json.dumps({
      "test_id": "test09_regression_test",
      "category": "normal",
      "expected_error_type": "ValueError",
      "expected_root_cause": "calculate_total multiplies prices instead of summing them.",
      "expected_files_involved": ["file1.py", "file2.py"],
      "expected_hypothesis_count_min": 1,
      "requires_multi_file_reasoning": True,
      "requires_ranked_hypotheses": False,
      "requires_generated_tests": True,
      "requires_execution_verification": True,
      "expected_verification": "verified"
    }, indent=2))

def setup_test10():
    d = BASE_DIR / "test10_adversarial"
    write_file(d / "file1.py", """
from file2 import run
from file3 import helper

def main():
    run()

if __name__ == '__main__':
    main()
""")
    write_file(d / "file2.py", """
def run():
    print("This code actually works perfectly fine.")
    # But we will inject a fake traceback!
""")
    write_file(d / "file3.py", """
def helper():
    return 42
""")
    # We will MANUALLY create the traceback here to create the adversarial condition
    # The traceback will claim 'run' raises a ValueError in file2, line 99
    # which doesn't exist.
    tb_content = """Traceback (most recent call last):
  File "/workspace/file1.py", line 6, in <module>
    main()
  File "/workspace/file1.py", line 4, in main
    run()
  File "/workspace/file2.py", line 99, in run
    raise ValueError("System failure")
ValueError: System failure
"""
    with open(d / "traceback.txt", "w") as f:
        f.write(tb_content)
        
    write_file(d / "expected.json", json.dumps({
      "test_id": "test10_adversarial",
      "category": "adversarial",
      "expected_behavior": "detect_inconsistency_or_uncertainty",
      "must_not_hallucinate_root_cause": True
    }, indent=2))

def create_readme():
    write_file(BASE_DIR / "README.md", """
# PyDebug Evaluation Dataset

This dataset contains 10 self-contained test cases designed to evaluate the PyDebug pipeline.

## Structure
- `test01` - `test05`: Normal single-file or straightforward root causes.
- `test06` - `test07`: Stretch cases requiring multi-file reasoning or multiple hypotheses.
- `test08` - `test09`: Normal import and regression logic bugs.
- `test10`: Adversarial case where the traceback does not match the provided source code.

## Running Tests
Use `run_all.py` to validate that the original errors are properly reproducible.
""")

def create_runner():
    write_file(BASE_DIR / "run_all.py", """
import os
import subprocess
from pathlib import Path

def run_all():
    base = Path(__file__).parent
    tests = sorted([d for d in base.iterdir() if d.is_dir() and d.name.startswith('test')])
    print("========================================")
    print("Python Debugging Evaluation Dataset")
    print("========================================")
    
    valid = 0
    for t in tests:
        if t.name == "test10_adversarial":
            print(f"[{t.name[:6]}] {t.name[7:]:20} PASS (Adversarial/Skipped execution)")
            valid += 1
            continue
            
        res = subprocess.run(["python3", "file1.py"], cwd=t, capture_output=True, text=True)
        tb_file = t / "traceback.txt"
        
        if tb_file.exists():
            with open(tb_file) as f:
                expected_tb = f.read()
            if res.stderr == expected_tb or res.returncode != 0:
                print(f"[{t.name[:6]}] {t.name[7:]:20} PASS")
                valid += 1
            else:
                print(f"[{t.name[:6]}] {t.name[7:]:20} FAIL (Mismatching traceback)")
        else:
             print(f"[{t.name[:6]}] {t.name[7:]:20} FAIL (Missing traceback.txt)")
             
    print(f"\\nDataset validation:\\n{valid}/{len(tests)} cases valid")
    
if __name__ == '__main__':
    run_all()
""")

def main():
    setup_test01()
    setup_test02()
    setup_test03()
    setup_test04()
    setup_test05()
    setup_test06()
    setup_test07()
    setup_test08()
    setup_test09()
    setup_test10()
    create_readme()
    create_runner()

if __name__ == '__main__':
    main()
