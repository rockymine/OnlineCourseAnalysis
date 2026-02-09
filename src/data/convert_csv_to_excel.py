import pandas as pd
import os
import glob


def csv_to_excel(csv_filepath, excel_filepath):
    """
    Convert a CSV file to an Excel file.

    Parameters:
    csv_filepath (str): The file path of the input CSV file.
    excel_filepath (str): The file path of the output Excel file.
    """
    df = pd.read_csv(csv_filepath)
    df.to_excel(excel_filepath, index=False)


def convert_all_csv_to_excel(csv_folder, excel_folder):
    """
    Convert all CSV files in a directory to Excel format.

    Parameters:
    csv_folder (str): The directory containing the input CSV files.
    excel_folder (str): The directory where the output Excel files will be saved.
    """
    # Get a list of all CSV files in the directory
    csv_files = glob.glob(os.path.join(csv_folder, "*.csv"))

    for csv_file in csv_files:
        # Get the base file name without the extension
        base_name = os.path.basename(csv_file).split('.')[0]
        # Construct the Excel file path
        excel_file = os.path.join(excel_folder, f"{base_name}.xlsx")
        # Convert the CSV file to Excel format
        csv_to_excel(csv_file, excel_file)


if __name__ == '__main__':
    convert_all_csv_to_excel('data/processed', 'data/processed')
