# is_even_from_2026 🚀

The most advanced, deterministic, and **absolutely massive** parity-checking library of 2026.

Why use the boring `% 2` operator when you can have **millions of lines** of hand-crafted `if` statements dynamically loaded from nested ZIP files?

## ✨ Features

- Ultra-precise even/odd detection for any integer
- Dynamically generated modules with individual `if` statements
- High-performance generator using multiprocessing and parallel I/O
- Nested ZIP compression for efficient storage
- Automatic resume from the last generated number
- Performance testing script included
- Optional automatic Git commit & push

## 📁 Project Structure
```text
is_even_from_2026/
└──is_even_from_2026/
    ├── init.py                     # Main package entry point (dynamic loader)
    ├── number_modules/             # Generated ZIP modules (organized in subfolders)
    ├── config_generator.py         # Configuration (step size, batch settings...)
├── generator.py                    # High-performance module generator
└── prova.py                        # Performance testing script
```

## 🚀 How to Generate More Numbers
### 1. Check Disk Space ⚠️
Each batch (~2000 files) adds approximately **100 MB** of data. Make sure you have enough free space.

### 2. Run the Generator

Generate the next batch:
```bash
python generator.py
python generator.py --commit #with autocmmit on github
```

## 🧪 Test the Performance
Run the included test script to benchmark the library:
```bash
python prova.py
```
The script will test several numbers (small, large, and very large) and show the execution time in milliseconds.

## 🤖 Contributing
1. Clone the repository
2. Run python generator.py (add --commit if you want to push automatically)
3. Commit and push your new modules
4. Help expand the largest is_even database in human history

Note: This project is a humorous demonstration of extreme over-engineering.
In any real application, just use number % 2 == 0.
Made with ❤️ and highly questionable life choices in 2026.
