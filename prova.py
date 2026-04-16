import time
from is_even_from_2026 import is_even

def test_is_even(number):
    """Esegue il test e stampa il risultato con il tempo di esecuzione."""
    start_time = time.perf_counter()
    try:
        risultato = is_even(number)
        end_time = time.perf_counter()
        
        # Calcolo tempo in millisecondi
        durata = (end_time - start_time) * 1000
        
        print(f"Numero: {number:<15} | Pari: {str(risultato):<10} | Tempo: {durata:>8.2f} ms")
    except Exception as e:
        print(f"Errore durante il test di {number}: {e}")

# --- ESECUZIONE TEST ---

print("-" * 60)
print(f"{'TEST DI PRESTAZIONE IS_EVEN':^60}")
print("-" * 60)

# Test 1: Numeri nel range (0.zip)
# La prima chiamata sarà la più lenta (caricamento dello zip)
test_is_even(42)
# La seconda chiamata allo stesso range sarà fulminea
test_is_even(7)

print("-" * 60)

# Test 2: Numero in un altro range (es. 1500000.zip)
test_is_even(1526859)

print("-" * 60)

# Test 3: Numero fuori range (file non esistente)
test_is_even(1000000000004)

print("-" * 60)