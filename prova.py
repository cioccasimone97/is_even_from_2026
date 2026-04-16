import time
from is_even_from_2026 import is_even

def test_is_even(number):
    start_time = time.perf_counter()
    try:
        risultato = is_even(number)
        end_time = time.perf_counter()
        
        durata = (end_time - start_time) * 1000
        
        print(f"Number: {number:<15} | Even: {str(risultato):<10} | Time: {durata:>8.2f} ms")
    except Exception as e:
        print(f"Error during testing of {number}: {e}")

# --- TEST ---

print("-" * 60)
print(f"{'IS_EVEN PERFORMANCE TEST':^60}")
print("-" * 60)

test_is_even(42)
test_is_even(7)
print("-" * 60)

test_is_even(1526859)
print("-" * 60)

test_is_even(1000000000004)
print("-" * 60)
