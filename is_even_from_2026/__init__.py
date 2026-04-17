import sys
import os
import importlib
import zipfile
from .config_generator import step, files_x_folder

def is_even(number: int) -> bool:
    if not isinstance(number, int):
        raise TypeError("Please enter an integer!")
        
    # 1. Calculate the base filename and the folder index
    base_range = (number // step) * step
    base_name = str(base_range)
    zip_name = f"{base_name}.zip"
    
    # Calculate the subfolder index
    file_position = base_range // step
    folder_index = str(file_position // files_x_folder)
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 2. Build the dynamic path
    outer_zip_path = os.path.join(
        current_dir, 
        "number_modules", 
        folder_index, 
        zip_name
    )

    if not os.path.exists(outer_zip_path):
        return f"Error: The file {zip_name} does not exist at {outer_zip_path}"

    # 3. Setup temporary directory
    temp_dir = os.path.join(current_dir, "temp_extracted")
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    
    inner_zip_path = os.path.join(temp_dir, zip_name)

    try:
        # 4. Extract the INNER ZIP from the OUTER ZIP
        with zipfile.ZipFile(outer_zip_path, 'r') as outer_zf:
            outer_zf.extract(zip_name, temp_dir)

        # 5. Dynamic import from the extracted ZIP
        if inner_zip_path not in sys.path:
            sys.path.insert(0, inner_zip_path)

        # Import the module (which shares the same name as the base number)
        module = importlib.import_module(base_name)
        importlib.reload(module)  # Reload to prevent cache issues if files change
        
        return module.is_even(number)

    except Exception as e:
        return f"Error: {e}"