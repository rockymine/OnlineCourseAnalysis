import subprocess

# Define a list of scripts to run in order
scripts = [
    'src/data/preprocess.py',
    'src/data/aggregate_by_unit.py',
    'src/data/aggregate_by_course.py',
    'src/data/convert_csv_to_excel.py',
    'src/visualization/visualize_by_unit.py',
    'src/visualization/visualize_by_course.py',
]

# Run each script
for script in scripts:
    subprocess.run(['python', script], check=True)
