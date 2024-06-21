import os
import glob
import shutil
from osgeo import gdal
import geopandas as gpd


def copy_and_clip_safe_folder(safe_folder, shp_file, output_folder):
    # Read the shapefile
    shp = gpd.read_file(shp_file)
    bbox = shp.total_bounds  # Get bounding box: (minx, miny, maxx, maxy)

    # Copy the entire .SAFE folder to the output directory
    safe_output_folder = os.path.join(output_folder, os.path.basename(safe_folder))
    shutil.copytree(safe_folder, safe_output_folder)

    # Find all JP2 files within the copied .SAFE folder
    band_files = glob.glob(os.path.join(safe_output_folder, 'GRANULE', '*', 'IMG_DATA', '*.jp2'))

    for band_file in band_files:
        # Output filename remains the same within the copied structure
        temp_file = band_file + '.tmp.jp2'

        # Clip the band file using gdalwarp
        gdal.Warp(
            temp_file, band_file, format='JP2OpenJPEG',
            outputBounds=(bbox[0], bbox[1], bbox[2], bbox[3]),
            cutlineDSName=shp_file, cropToCutline=True
        )

        # Replace original file with the clipped file
        os.remove(band_file)
        os.rename(temp_file, band_file)


def main(input_dir, shp_file, output_dir):
    safe_folders = glob.glob(os.path.join(input_dir, "*", "S2*_MSIL1C*.SAFE"))

    for safe_folder in safe_folders:
        # Clip the .SAFE folder and copy to output directory
        copy_and_clip_safe_folder(safe_folder, shp_file, output_dir)

if __name__ == "__main__":
    input_dir = r'C:\Users\mrmuf\Documents\Aotea_test_files\Sentinel\Sentinel_Raw_Data'
    shp_file = r'C:\Users\mrmuf\Documents\Aotea_test_files\Sentinel\aotea_s2_aoi'
    output_dir = r'C:\Users\mrmuf\Documents\Aotea_test_files\Sentinel\Sentinel_Trimmed_Data'

    main(input_dir, shp_file, output_dir)
