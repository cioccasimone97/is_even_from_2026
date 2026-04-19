import os
import zipfile
import io
import subprocess
import argparse
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from is_even_from_2026.config_generator import step, files_to_generate, files_x_folder
import gc

def generate_batch_modules(batch_params_list):
    """
    Generates a batch of modules in a single process to reduce IPC overhead.
    Uses minimum compression level (1) for maximum speed.
    """
    batch_results = []
    
    gc.disable()
    
    for params in batch_params_list:
        start, end, target_subfolder = params
        base_name = f"{start}"
        py_filename = f"{base_name}.py"
        inner_zip_filename = f"{base_name}.zip"
        
        # 1. Generate .py content
        lines = ["def is_even(number: int) -> bool:\n"]
        lines.extend([
            f"    if number == {i}: return {i % 2 == 0}\n" 
            for i in range(start, end)
        ])
        py_content = "".join(lines)

        # 2. Create INNER ZIP
        inner_zip_buffer = io.BytesIO()
        with zipfile.ZipFile(inner_zip_buffer, "w", zipfile.ZIP_DEFLATED) as inner_zf:
            inner_zf.writestr(py_filename, py_content)
        inner_zip_bytes = inner_zip_buffer.getvalue()

        # 3. Create OUTER ZIP
        outer_zip_buffer = io.BytesIO()
        with zipfile.ZipFile(outer_zip_buffer, "w", zipfile.ZIP_DEFLATED) as outer_zf:
            outer_zf.writestr(inner_zip_filename, inner_zip_bytes)
        
        final_zip_bytes = outer_zip_buffer.getvalue()
        final_path = os.path.join(target_subfolder, inner_zip_filename)
        
        batch_results.append((final_path, final_zip_bytes))
    
    gc.enable()
    
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
    batch_size = max(10, len(tasks) // cpu_count)
    
    # Split tasks into dynamic batches
    batches = [tasks[i:i + batch_size] for i in range(0, len(tasks), batch_size)]
    
    all_generated_files = []
    print(f"🚀 Generation: {len(tasks)} files | CPUs: {cpu_count} | Batch Size: {batch_size}")
    
    # --- PHASE 1 & 2: Concurrent Generation and Eager Writing ---
    # We use a ProcessPool for CPU-bound generation (math/compression) 
    # and a ThreadPool for I/O-bound disk writing.
    with ProcessPoolExecutor(max_workers=cpu_count) as executor:
        # Schedule all batch generation tasks
        futures = [executor.submit(generate_batch_modules, b) for b in batches]
        
        # Initialize the progress bar based on the total number of FILES (not batches)
        # for high-granularity visual feedback.
        pbar = tqdm(total=len(tasks), desc="Processing", unit="file")
        
        # We use a ThreadPool to flush data to disk without blocking the CPU processes
        with ThreadPoolExecutor(max_workers=min(32, cpu_count + 3)) as writer_pool:
            for future in as_completed(futures):
                # Retrieve the list of (path, binary_data) from the completed process
                batch_data = future.result()
                
                # Helper function to perform the write and increment the progress bar immediately
                def write_and_update(data):
                    write_to_disk(data)
                    pbar.update(1) # Updates the UI for every single file written
                
                # Map the writing task across the thread pool for the current batch.
                # Using list() or consuming the map ensures execution before the next batch loop.
                list(writer_pool.map(write_and_update, batch_data))
        
        pbar.close()

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