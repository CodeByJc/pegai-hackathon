# PyDebug Evaluation Dataset

This dataset contains 10 self-contained test cases designed to evaluate the PyDebug pipeline.

## Structure
- `test01` - `test05`: Normal single-file or straightforward root causes.
- `test06` - `test07`: Stretch cases requiring multi-file reasoning or multiple hypotheses.
- `test08` - `test09`: Normal import and regression logic bugs.
- `test10`: Adversarial case where the traceback does not match the provided source code.

## Running Tests
Use `run_all.py` to validate that the original errors are properly reproducible.
