import sys
import os
import importlib
import zipfile

def is_even(number: int) -> bool:
    if not isinstance(number, int):
        raise TypeError("Inserisci un numero intero!")
        
    STEP = 1_000_000
    base_range = (number // STEP) * STEP
    nome_base = str(base_range)
    nome_zip = f"{nome_base}.zip"
    
    cartella_attuale = os.path.dirname(os.path.abspath(__file__))
    
    # 1. Trova il file ZIP ESTERNO (fisico)
    percorso_zip_esterno = os.path.join(cartella_attuale, "is_even_from_2026", "moduli_numeri", nome_zip)

    if not os.path.exists(percorso_zip_esterno):
        percorso_zip_alternativo = os.path.join(cartella_attuale, "moduli_numeri", nome_zip)
        if os.path.exists(percorso_zip_alternativo):
            percorso_zip_esterno = percorso_zip_alternativo
        else:
            return f"Errore: Il file {nome_zip} non esiste nei percorsi previsti."

    # 2. Setup cartella temporanea per lo ZIP INTERNO
    temp_dir = os.path.join(cartella_attuale, "temp_extracted")
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    
    percorso_zip_interno = os.path.join(temp_dir, nome_zip)

    try:
        # 3. Estrazione: Leggiamo lo ZIP esterno per estrarre lo ZIP interno
        with zipfile.ZipFile(percorso_zip_esterno, 'r') as z_esterno:
            if nome_zip in z_esterno.namelist():
                z_esterno.extract(nome_zip, temp_dir)
            else:
                return f"Errore: Lo zip interno {nome_zip} non è presente dentro lo zip esterno."

        # 4. IL PUNTO CHIAVE: percorso_zip deve puntare al file estratto
        # Python può importare moduli direttamente da file .zip se sono in sys.path
        percorso_zip = percorso_zip_interno 

        if percorso_zip not in sys.path:
            sys.path.insert(0, percorso_zip)

        # 5. Importazione del file .py contenuto nel secondo ZIP
        # Python cercherà 'nome_base.py' dentro 'percorso_zip' (che è il secondo archivio)
        modulo = importlib.import_module(nome_base)
        importlib.reload(modulo)
        
        return modulo.is_even(number)

    except Exception as e:
        return f"Errore critico durante l'estrazione o l'importazione: {e}"