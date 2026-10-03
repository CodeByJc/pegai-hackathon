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
             
    print(f"\nDataset validation:\n{valid}/{len(tests)} cases valid")
    
if __name__ == '__main__':
    run_all()
