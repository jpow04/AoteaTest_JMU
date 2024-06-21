import os
import subprocess

def process_landsat_data(input_dir, output_dir):
    # Ensure the input and output directories exist
    if not os.path.exists(input_dir):
        raise FileNotFoundError(f"Input directory '{input_dir}' not found.")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Loop through all files in the input directory
    for file in os.listdir(input_dir):
        if file.endswith(".tar"):  # Check if the file is a Landsat tar.gz archive
            file_path = os.path.join(input_dir, file)
            output_file_path = os.path.join(output_dir, os.path.splitext(file)[0])

            # ARCSI command for atmospheric correction, AOT estimation, cloud masking, and metadata production
            arcsi_command = [
                "arcsi.py",
                "--sensor", "landsatoli",  # Assuming Landsat 8 OLI sensor, adjust for other sensors
                "--srcfile", file_path,
                "--output", output_file_path,
                "--outfor", "GTiff",  # Output format as GeoTIFF
                "--aero", "auto",  # Automatic AOT estimation
                "--cloud", "true",  # Cloud masking enabled
                "--metadata", "true",  # Produce metadata file
                "--tmpath", "/tmp"  # Temporary path for processing, can be adjusted
            ]

            # Complete command with conda environment activation
            command = f"conda run -n arcsienv {' '.join(arcsi_command)}"

            # Execute the command
            try:
                subprocess.run(command, shell=True, check=True)
                print(f"Successfully processed {file_path}")
            except subprocess.CalledProcessError as e:
                print(f"Error processing {file_path}: {e}")

if __name__ == "__main__":
    input_directory = r"C:\Users\mrmuf\Documents\Aotea_test_files\Landsat_test"  # Specify your input directory
    output_directory = r"C:\Users\mrmuf\Documents\Aotea_test_files\Landsat_test\Processed Landsat"  # Specify your output directory
    process_landsat_data(input_directory, output_directory)
