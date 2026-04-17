import sys
import os
import importlib
import zipfile
from .config_generator import step, files_x_folder # Import relativo se sei nel package

def is_even(number: int) -> bool:
    if not isinstance(number, int):
        raise TypeError("Inserisci un numero intero!")
        
    # 1. Calcolo del nome file e dell'indice della cartella
    base_range = (number // step) * step
    nome_base = str(base_range)
    nome_zip = f"{nome_base}.zip"
    
    # Calcolo dell'indice della cartella (fondamentale!)
    # Se i file sono generati progressivamente, l'indice è: 
    # (posizione_del_file) // files_x_folder
    posizione_file = base_range // step
    folder_index = str(posizione_file // files_x_folder)
    
    cartella_attuale = os.path.dirname(os.path.abspath(__file__))
    
    # 2. Costruzione del percorso dinamico
    # Il percorso deve includere la sottocartella numerata (0, 1, 2...)
    percorso_zip_esterno = os.path.join(
        cartella_attuale, 
        "number_modules", 
        folder_index, 
        nome_zip
    )

    if not os.path.exists(percorso_zip_esterno):
        return f"Errore: Il file {nome_zip} non esiste in {percorso_zip_esterno}"

    # 3. Setup cartella temporanea
    temp_dir = os.path.join(cartella_attuale, "temp_extracted")
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    
    percorso_zip_interno = os.path.join(temp_dir, nome_zip)

    try:
        # 4. Estrazione dello ZIP interno dallo ZIP esterno
        with zipfile.ZipFile(percorso_zip_esterno, 'r') as z_esterno:
            z_esterno.extract(nome_zip, temp_dir)

        # 5. Importazione dinamica dallo ZIP estratto
        if percorso_zip_interno not in sys.path:
            sys.path.insert(0, percorso_zip_interno)

        # Importiamo il modulo (che ha lo stesso nome del numero base)
        modulo = importlib.import_module(nome_base)
        importlib.reload(modulo) # Ricarica per evitare cache se i file cambiano
        
        return modulo.is_even(number)

    except Exception as e:
        return f"Errore: {e}"