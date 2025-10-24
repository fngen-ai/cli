import os
from pathlib import Path
import shutil

def copy_example_package(assets_path, destination_dir):
    current_file = os.path.abspath(__file__)
    current_dir = os.path.dirname(current_file)
    src_dir = os.path.join(current_dir, assets_path)

    final_package_dir = os.path.join(destination_dir, assets_path)

    shutil.copytree(src_dir, final_package_dir, dirs_exist_ok=True)

    return final_package_dir
