import os
import zipfile
import io
from concurrent.futures import ProcessPoolExecutor

def genera_singolo_modulo(params):
    "Generate the Matryoshka structure: OuterZip -> InnerZip -> Number.py"
    start, end, folder = params
    nome_base = f"{start}"
    file_py = f"{nome_base}.py"
    nome_zip = f"{nome_base}.zip"
    percorso_finale_zip = os.path.join(folder, nome_zip)
    
    # --- 1. Generate the content of the .py file ---
    buffer_py = [f"def is_even(number: int) -> bool:\n"]
    for i in range(start, end):
        risultato = "True" if i % 2 == 0 else "False"
        buffer_py.append(f"    if number == {i}: return {risultato}\n")
    contenuto_py = "".join(buffer_py)

    # --- 2. Create the INNER ZIP in memory (RAM) ---
    buffer_zip_interno = io.BytesIO()
    with zipfile.ZipFile(buffer_zip_interno, "w", zipfile.ZIP_DEFLATED) as zf_interno:
        zf_interno.writestr(file_py, contenuto_py)
    byte_zip_interno = buffer_zip_interno.getvalue()

    # --- 3. Create the OUTER ZIP on disk and insert the inner ZIP ---
    with zipfile.ZipFile(percorso_finale_zip, "w", zipfile.ZIP_DEFLATED) as zf_esterno:
        zf_esterno.writestr(nome_zip, byte_zip_interno)
    
    return f"✅ Matryoshka created: {percorso_finale_zip} (contains {nome_zip} -> {file_py})"

def trova_ultimo_numero(folder):
    "Find the highest number among the existing .zip files."
    if not os.path.exists(folder) or not os.listdir(folder):
        return -1_000_000 
    
    files = os.listdir(folder)
    numeri = []
    for f in files:
        if f.endswith(".zip"):
            nome_senza_ext = f.replace(".zip", "")
            if nome_senza_ext.isdigit():
                numeri.append(int(nome_senza_ext))
    
    return max(numeri) if numeri else -1_000_000

def genera_moduli_progressivi():
    folder = os.path.join("is_even_from_2026", "moduli_numeri")
    os.makedirs(folder, exist_ok=True)
    
    step = 1_000_000
    numero_file_da_generare = 2000 
    
    ultimo_start = trova_ultimo_numero(folder)
    prossimo_start = ultimo_start + step
    
    tasks = []
    for i in range(numero_file_da_generare):
        start = prossimo_start + (i * step)
        end = start + step
        tasks.append((start, end, folder))

    print(f"📂 Target folder: {folder}")
    print(f"🚀 Resuming from: {prossimo_start}")
    print(f"📦 Generating Matryoshka (Zip-in-Zip)...")

    with ProcessPoolExecutor(max_workers=None) as executor:
        for result in executor.map(genera_singolo_modulo, tasks):
            print(result)

if __name__ == "__main__":
    genera_moduli_progressivi()
