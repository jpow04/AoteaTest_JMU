import subprocess
import os
import glob
import re
import shutil

# Paths and directories
sen2cor_dir = r"C:\Users\mrmuf\Documents\Aotea_data_Processor\Sen2Cor-02.11.00-win64"   # Directory where Sen2Cor is located
input_dir = r"C:\Users\mrmuf\Documents\Aotea_test_files\Sentinel\Sentinel_Raw_Data"  # Directory containing L1C data
output_dir = r"C:\Users\mrmuf\Documents\Aotea_test_files\Sentinel\Sentinel_Processed_Data" # Directory for output L2A data

if not os.path.exists(output_dir):  # Find output directory or create one if it does not exist
    os.makedirs(output_dir)
    print("Sentinel processed data directory created successfully")
else:
    print("Sentinel processed data directory already exists")

# Function to move .SAFE files out of their containing folders and remove empty folders
def organize_safe_files(base_dir):
    print("Organizing datasets")
    for year_dir in os.listdir(base_dir):
        year_path = os.path.join(base_dir, year_dir)
        if os.path.isdir(year_path):
            for folder in os.listdir(year_path):
                folder_path = os.path.join(year_path, folder)
                if os.path.isdir(folder_path):
                    safe_files = glob.glob(os.path.join(folder_path, "S2*_MSIL1C*.SAFE"))
                    for safe_file in safe_files:
                        new_location = os.path.join(year_path, os.path.basename(safe_file))
                        shutil.move(safe_file, new_location)
                        print(f"Moved {safe_file} to {new_location}")

                    # Remove the now-empty folder if it's empty
                    if not os.listdir(folder_path):  # Check if the folder is empty
                        os.rmdir(folder_path)
                        print(f"Removed empty folder {folder_path}")

# Function to list unique year folders in the input directory
def list_year_folders(input_dir):
    l1c_products = glob.glob(os.path.join(input_dir, "*", "S2*_MSIL1C*.SAFE"))
    years = set()

    for l1c_product in l1c_products:
        match = re.search(r'S2[AB]_MSIL1C_(\d{4})', l1c_product)
        if match:
            year = match.group(1)
            years.add(year)

    print("Identified year datasets:")
    for year in sorted(years):
        print(year)

    return l1c_products  # Return the full paths for processing

# Function to list all datasets to be processed
def list_datasets(input_dir):
    l1c_products = glob.glob(os.path.join(input_dir, "*", "S2*_MSIL1C*.SAFE"))
    datasets = []

    for l1c_product in l1c_products:
        match = re.search(r'S2[AB]_MSIL1C_(\d{4})', l1c_product)
        if match:
            datasets.append(os.path.basename(l1c_product))

    print("Datasets to be processed:")
    for dataset in datasets:
        print(dataset)

    # Display the number of identified datasets
    print(f"\nTotal number of datasets identified: {len(datasets)}")

    return l1c_products  # Return the full paths for processing

# Function to run Sen2Cor on a specified L1C product
def run_sen2cor(l1c_product_path):
    original_dir = os.getcwd()  # Save the current working directory
    try:
        os.chdir(sen2cor_dir)  # Change to the Sen2Cor directory
        sen2cor_command = os.path.join(sen2cor_dir, "L2A_Process.bat")
        command = [sen2cor_command, l1c_product_path]

        # Print the command for debugging purposes
        print(f"Running command: {' '.join(command)}")

        # Run the command and capture output and errors in real-time
        with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                              shell=True) as process:
            for line in process.stdout:
                print(line, end='')  # Print each line of stdout as it is produced

            for line in process.stderr:
                print(line, end='')  # Print each line of stderr as it is produced

        process.wait()  # Wait for the process to complete

        if process.returncode != 0:
            raise RuntimeError(f"Sen2Cor processing failed for {l1c_product_path}")

        print(f"Sen2Cor processing completed for {l1c_product_path}")
    finally:
        os.chdir(original_dir)  # Change back to the original directory

# Function to move L2A data to the output directory within a year folder
def move_l2a_data(input_dir):
    l2a_products = glob.glob(os.path.join(input_dir, "*", "S2*_MSIL2A*.SAFE"))
    l2a_datasets = []

    for l2a_product in l2a_products:
        match = re.search(r'S2[AB]_MSIL2A_(\d{4})', l2a_product)
        if match:
            l2a_datasets.append(os.path.basename(l2a_product))
            year = match.group(1)
            year_folder = os.path.join(output_dir, year)
            os.makedirs(year_folder, exist_ok=True)  # Create the year folder if it doesn't exist

            new_location = os.path.join(year_folder, os.path.basename(l2a_product))
            shutil.move(l2a_product, new_location)
            print(f"Moved L2A data to {new_location}")
        else:
            print(f"Could not determine year for {l2a_products}")
    else:
        print(f"No remaining L2A data found")

# Main script
organize_safe_files(input_dir)  # Organize .SAFE files
list_year_folders(input_dir)  # Identify and list year folders
datasets = list_datasets(input_dir)  # Identify and list datasets to be processed
processed_count = 0  # Counter for processed datasets
# Prompt for confirmation
while True:
    user_input = input("Do you want to proceed with processing the identified datasets? (Y/N): ").strip().upper()
    if user_input == 'Y':
        if datasets:
            for dataset in datasets:
                # Run Sen2Cor to process the first L1C dataset to L2A
                run_sen2cor(dataset)

                # Move the L2A data to the output directory within the appropriate year folder
                l2a_datasets = move_l2a_data(input_dir)

                processed_count += 1  # Increment the processed count

        else:
            print("No datasets found to process.")
        break
    elif user_input == 'N':
        print("Processing aborted by the user.")
        break
    else:
        print("Invalid input. Please enter 'Y' to proceed or 'N' to abort.")

# Final message indicating processing completion
print(f"\nProcessing complete. Total number of processed datasets: {processed_count}")