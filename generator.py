import os
import zipfile
import io
from concurrent.futures import ProcessPoolExecutor
from is_even_from_2026.config_generator import step, files_to_generate, files_x_folder
import subprocess
import sys
import argparse
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor, as_completed

def generate_single_module(params):
    """
    Generate the Matryoshka structure: Subfolder -> OuterZip -> InnerZip -> Number.py
    """
    start, end, target_subfolder = params
    base_name = f"{start}"
    py_file = f"{base_name}.py"
    zip_name = f"{base_name}.zip"
    
    # Ensure the specific numbered subfolder exists
    os.makedirs(target_subfolder, exist_ok=True)
    
    final_zip_path = os.path.join(target_subfolder, zip_name)
    
    # --- 1. Generate the content of the .py file ---
    py_buffer = [f"def is_even(number: int) -> bool:\n"]
    for i in range(start, end):
        result = "True" if i % 2 == 0 else "False"
        py_buffer.append(f"    if number == {i}: return {result}\n")
    py_content = "".join(py_buffer)

    # --- 2. Create the INNER ZIP in memory (RAM) ---
    inner_zip_buffer = io.BytesIO()
    with zipfile.ZipFile(inner_zip_buffer, "w", zipfile.ZIP_DEFLATED) as inner_zf:
        inner_zf.writestr(py_file, py_content)
    inner_zip_bytes = inner_zip_buffer.getvalue()

    # --- 3. Create the OUTER ZIP on disk and insert the inner ZIP ---
    with zipfile.ZipFile(final_zip_path, "w", zipfile.ZIP_DEFLATED) as outer_zf:
        outer_zf.writestr(zip_name, inner_zip_bytes)
    
    return f"✅ Matryoshka created: {final_zip_path}"

def get_stats(base_path):
    """
    Scan subfolders to find the total count of .zip files and the highest number used.
    """
    total_files = 0
    max_num = -step
    
    if not os.path.exists(base_path):
        return 0, max_num

    for root, dirs, files in os.walk(base_path):
        for f in files:
            if f.endswith(".zip"):
                total_files += 1
                name_without_ext = f.replace(".zip", "")
                if name_without_ext.isdigit():
                    max_num = max(max_num, int(name_without_ext))
                    
    return total_files, max_num

def generate_progressive_modules(do_commit=False):
    """Main logic to manage multiprocessing generation and Git sync."""
    base_folder = os.path.join("is_even_from_2026", "number_modules")
    total_existing, last_val = get_stats(base_folder)
    next_start = last_val + step
    
    tasks = []
    for i in range(files_to_generate):
        start = next_start + (i * step)
        end = start + step
        folder_index = (total_existing + i) // files_x_folder
        target_subfolder = os.path.join(base_folder, str(folder_index))
        tasks.append((start, end, target_subfolder))

    # Calculate the highest value reached in this session
    max_value_generated = next_start + ((files_to_generate - 1) * step)

    # Multiprocessing execution with tqdm progress bar
    with ProcessPoolExecutor(max_workers=None) as executor:
        futures = [executor.submit(generate_single_module, t) for t in tasks]
        
        for _ in tqdm(as_completed(futures), total=len(futures), desc="Generating modules", unit="file"):
            pass

    if do_commit:
        git_automatic_push(max_value_generated)

def git_automatic_push(max_val):
    """Performs git add, commit, and push with descriptive console updates."""
    commit_message = f"Update: {max_val}"
    
    try:
        print("\n--- 🤖 Starting Git synchronization ---")
        
        # Stage all changes
        print("--- 🤖 Running: git add . ---")
        subprocess.run(["git", "add", "."], check=True)
        
        # Commit the changes
        print(f"--- 🤖 Running: git commit -m '{commit_message}' ---")
        subprocess.run(["git", "commit", "-m", commit_message], check=True)
        
        # Push to remote repository
        print("--- 🤖 Running: git push ---")
        subprocess.run(["git", "push"], check=True)
        
        print("✅ Repository updated successfully!")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Git error occurred: {e}")
    except Exception as e:
        print(f"⚠️ An unexpected error occurred: {e}")

if __name__ == "__main__":
    #Clean window
    os.system('cls' if os.name == 'nt' else 'clear')
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--commit", action="store_true")
    args = parser.parse_args()
    
    generate_progressive_modules(do_commit=args.commit)