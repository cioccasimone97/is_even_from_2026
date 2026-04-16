import os
import zipfile
import io
from concurrent.futures import ProcessPoolExecutor

def genera_singolo_modulo(params):
    """Genera la struttura Matrioska: ZipEsterno -> ZipInterno -> Numero.py"""
    start, end, folder = params
    nome_base = f"{start}"
    file_py = f"{nome_base}.py"
    nome_zip = f"{nome_base}.zip" # Nome usato sia per l'interno che per l'esterno
    percorso_finale_zip = os.path.join(folder, nome_zip)
    
    # --- 1. Generiamo il contenuto del file .py ---
    buffer_py = [f"def is_even(number: int) -> bool:\n"]
    for i in range(start, end):
        risultato = "True" if i % 2 == 0 else "False"
        buffer_py.append(f"    if number == {i}: return {risultato}\n")
    contenuto_py = "".join(buffer_py)

    # --- 2. Creiamo lo ZIP INTERNO in memoria (RAM) ---
    # Usiamo un BytesIO per non scrivere file intermedi inutili sul disco
    buffer_zip_interno = io.BytesIO()
    with zipfile.ZipFile(buffer_zip_interno, "w", zipfile.ZIP_DEFLATED) as zf_interno:
        zf_interno.writestr(file_py, contenuto_py)
    
    # Recuperiamo i byte dello zip appena creato
    byte_zip_interno = buffer_zip_interno.getvalue()

    # --- 3. Creiamo lo ZIP ESTERNO su disco e inseriamo lo ZIP interno ---
    with zipfile.ZipFile(percorso_finale_zip, "w", zipfile.ZIP_DEFLATED) as zf_esterno:
        # Scriviamo i byte dello zip interno chiamandolo con lo stesso nome .zip
        zf_esterno.writestr(nome_zip, byte_zip_interno)
    
    return f"✅ Matrioska creata: {percorso_finale_zip} (contiene {nome_zip} -> {file_py})"

def trova_ultimo_numero(folder):
    """Cerca il numero più alto tra i file .zip esistenti."""
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

    print(f"📂 Cartella target: {folder}")
    print(f"🚀 Riprendo da: {prossimo_start}")
    print(f"📦 Generazione Matrioska (Zip in Zip) in corso...")

    with ProcessPoolExecutor(max_workers=None) as executor:
        for result in executor.map(genera_singolo_modulo, tasks):
            print(result)

if __name__ == "__main__":
    genera_moduli_progressivi()