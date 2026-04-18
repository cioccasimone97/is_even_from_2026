import os
import zipfile
import io
import subprocess
import argparse
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
# Ensure these imports match your actual project structure
from is_even_from_2026.config_generator import step, files_to_generate, files_x_folder

def generate_batch_modules(batch_params_list):
    """
    Generates a batch of modules in a single process to reduce IPC overhead.
    Uses minimum compression level (1) for maximum speed.
    """
    batch_results = []
    
    for params in batch_params_list:
        start, end, target_subfolder = params
        base_name = f"{start}"
        py_filename = f"{base_name}.py"
        inner_zip_filename = f"{base_name}.zip"
        
        # 1. Generate .py content
        py_buffer = [f"def is_even(number: int) -> bool:\n"]
        for i in range(start, end):
            is_even = "True" if i % 2 == 0 else "False"
            py_buffer.append(f"    if number == {i}: return {is_even}\n")
        py_content = "".join(py_buffer)

        # 2. Create INNER ZIP (Fastest compression: level 1)
        inner_zip_buffer = io.BytesIO()
        with zipfile.ZipFile(inner_zip_buffer, "w", zipfile.ZIP_DEFLATED) as inner_zf:
            inner_zf.writestr(py_filename, py_content)
        inner_zip_bytes = inner_zip_buffer.getvalue()

        # 3. Create OUTER ZIP (Fastest compression: level 1)
        outer_zip_buffer = io.BytesIO()
        with zipfile.ZipFile(outer_zip_buffer, "w", zipfile.ZIP_DEFLATED) as outer_zf:
            outer_zf.writestr(inner_zip_filename, inner_zip_bytes)
        
        final_zip_bytes = outer_zip_buffer.getvalue()
        final_path = os.path.join(target_subfolder, inner_zip_filename)
        
        batch_results.append((final_path, final_zip_bytes))
        
    return batch_results

def get_stats(base_path):
    """Scans subfolders for existing modules and returns count and max value."""
    total_files = 0
    max_num = -step
    if not os.path.exists(base_path):
        return 0, max_num

    for root, dirs, files in os.walk(base_path):
        for f in files:
            if f.endswith(".zip"):
                total_files += 1
                name = f.replace(".zip", "")
                if name.isdigit():
                    max_num = max(max_num, int(name))
    return total_files, max_num

def write_to_disk(file_data):
    """Helper function for parallel disk writing."""
    path, data = file_data
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(data)

def generate_progressive_modules(do_commit=False):
    """Main logic managing batch multiprocessing and parallel disk I/O."""
    base_folder = os.path.join("is_even_from_2026", "number_modules")
    total_existing, last_val = get_stats(base_folder)
    next_start = last_val + step
    
    # 1. Define tasks
    tasks = []
    for i in range(files_to_generate):
        start = next_start + (i * step)
        end = start + step
        folder_index = (total_existing + i) // files_x_folder
        target_subfolder = os.path.join(base_folder, str(folder_index))
        tasks.append((start, end, target_subfolder))

    max_value_generated = next_start + ((files_to_generate - 1) * step)
    
    # --- DYNAMIC BATCH SIZE CALCULATION ---
    cpu_count = os.cpu_count() or 1
    # We want at least 4 batches per CPU core to keep them busy
    # but we also want at least 1 file per batch
    multiplier = 4
    batch_size = max(1, len(tasks) // (cpu_count * multiplier))
    
    # Split tasks into dynamic batches
    batches = [tasks[i:i + batch_size] for i in range(0, len(tasks), batch_size)]
    
    all_generated_files = []
    print(f"🚀 Generation: {len(tasks)} files | CPUs: {cpu_count} | Batch Size: {batch_size}")
    
    # --- PHASE 1: Parallel Generation in RAM ---
    with ProcessPoolExecutor(max_workers=cpu_count) as executor:
        futures = [executor.submit(generate_batch_modules, b) for b in batches]
        for future in tqdm(as_completed(futures), total=len(futures), desc="Generating (RAM)", unit="batch"):
            all_generated_files.extend(future.result())

    # --- PHASE 2: Parallel Disk Write ---
    print(f"\n💾 Flushing {len(all_generated_files)} files to disk...")
    # Increase workers for I/O if you have a fast NVMe SSD
    with ThreadPoolExecutor(max_workers=cpu_count * 2) as disk_executor:
        list(tqdm(disk_executor.map(write_to_disk, all_generated_files), 
                  total=len(all_generated_files), desc="Writing (Disk)"))

    if do_commit:
        git_automatic_push(max_value_generated)

def git_automatic_push(max_val):
    """Handles Git synchronization."""
    commit_message = f"Update: {max_val}"
    try:
        print("\n--- 🤖 Starting Git synchronization ---")
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", commit_message], check=True)
        subprocess.run(["git", "push"], check=True)
        print("✅ Repository updated successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Git error: {e}")

if __name__ == "__main__":
    os.system('cls' if os.name == 'nt' else 'clear')
    parser = argparse.ArgumentParser(description="High-performance IsEven Module Generator")
    parser.add_argument("--commit", action="store_true", help="Push to Git after generation")
    args = parser.parse_args()
    
    generate_progressive_modules(do_commit=args.commit)