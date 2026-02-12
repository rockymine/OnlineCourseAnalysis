import subprocess

# Define a list of scripts to run in order
scripts = [
    'src/data/preprocess.py',
    'src/data/aggregate_by_unit.py',
    'src/data/aggregate_by_course.py',
    'src/data/convert_csv_to_excel.py',
]

# Visualization scripts use relative imports and must be run as modules
modules = [
    'src.visualization.visualize_by_unit',
    'src.visualization.visualize_by_course',
]

# Run each script
for script in scripts:
    subprocess.run(['python', script], check=True)

# Run each module
for module in modules:
    subprocess.run(['python', '-m', module], check=True)
