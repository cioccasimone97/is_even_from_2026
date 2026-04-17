import os
import zipfile
import io
from concurrent.futures import ProcessPoolExecutor

def generate_single_module(params):
    """Generate the Matryoshka structure: OuterZip -> InnerZip -> Number.py"""
    start, end, folder = params
    base_name = f"{start}"
    py_file = f"{base_name}.py"
    zip_name = f"{base_name}.zip"
    final_zip_path = os.path.join(folder, zip_name)
    
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
    
    return f"✅ Matryoshka created: {final_zip_path} (contains {zip_name} -> {py_file})"

def find_last_number(folder):
    """Find the highest number among the existing .zip files."""
    if not os.path.exists(folder) or not os.listdir(folder):
        return -1_000_000 
    
    files = os.listdir(folder)
    numbers = []
    for f in files:
        if f.endswith(".zip"):
            name_without_ext = f.replace(".zip", "")
            if name_without_ext.isdigit():
                numbers.append(int(name_without_ext))
    
    return max(numbers) if numbers else -1_000_000

def generate_progressive_modules():
    folder = os.path.join("is_even_from_2026", "number_modules")
    os.makedirs(folder, exist_ok=True)
    
    step = 1_000_000
    files_to_generate = 2000 
    
    last_start = find_last_number(folder)
    next_start = last_start + step
    
    tasks = []
    for i in range(files_to_generate):
        start = next_start + (i * step)
        end = start + step
        tasks.append((start, end, folder))

    print(f"📂 Target folder: {folder}")
    print(f"🚀 Resuming from: {next_start}")
    print(f"📦 Generating Matryoshka (Zip-in-Zip)...")

    with ProcessPoolExecutor(max_workers=None) as executor:
        for result in executor.map(generate_single_module, tasks):
            print(result)

if __name__ == "__main__":
    generate_progressive_modules()