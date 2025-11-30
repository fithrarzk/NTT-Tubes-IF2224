# NTT-Tubes-IF2224: Compiler Pascal-S

Compiler untuk bahasa pemrograman Pascal-S dengan keyword dalam Bahasa Indonesia. Program ini mengimplementasikan tiga tahap utama compiler: Lexical Analysis, Syntax Analysis, dan Semantic Analysis.

![image](https://drive.google.com/uc?export=view&id=1r5alsMi9YbsmCQTMUXw2Qkhu6ybrMVms)

## Identitas Kelompok

| Nama | NIM |
| :--- | :--- |
| Indah Novita Tangdililing | 13523047 |
| Muhammad Fithra Rizki | 13523049 |
| Sakti Bimasena | 13523053 |
| Muhammad Timur Kanigara | 13523055 |
| Kefas Kurnia Jonathan | 13523113 |
---

## Deskripsi Program

Program ini adalah implementasi **Compiler** untuk bahasa pemrograman Pascal-S dengan keyword dalam Bahasa Indonesia. Compiler ini terdiri dari tiga tahap utama:

### 1. Lexical Analysis (Milestone 1)
**Lexer** membaca file kode sumber Pascal-S (`.pas`) dan mengubahnya dari rangkaian karakter mentah menjadi daftar **token** yang bermakna. Lexer diimplementasikan menggunakan **Deterministic Finite Automaton (DFA)** yang aturan transisinya dibaca dari file konfigurasi eksternal (`dfa_rules.json`). Program menyimulasikan DFA untuk mengenali *lexeme* dan mengklasifikasikannya ke dalam tipe token yang sesuai (misalnya `KEYWORD`, `IDENTIFIER`, `NUMBER`, `OPERATOR`, dll.).

**File terkait:** `lexer.py`, `dfa_load.py`, `token.py`, `dfa_rules.json`

### 2. Syntax Analysis (Milestone 2)
**Parser** melakukan analisis sintaks menggunakan metode **Recursive Descent Parsing** dengan pendekatan **LL(1) grammar**. Parser memvalidasi apakah rangkaian token mengikuti aturan tata bahasa Pascal-S yang telah didefinisikan.

**File terkait:** `parser.py`

### 3. Semantic Analysis (Milestone 3)
**Semantic Analyzer** melakukan analisis semantik dengan membangun **Abstract Syntax Tree (AST)** dari hasil parsing, lalu menggunakan **Symbol Table** dan **Type Checker** untuk validasi. Symbol Table menggunakan sistem tiga tabel (tab, btab, atab) untuk menyimpan informasi variabel, prosedur, fungsi, dan array. Type Checker menggunakan **Visitor Pattern** untuk melakukan traversal AST dan memvalidasi:
- Deklarasi variabel dan fungsi
- Kesesuaian tipe data pada operasi dan assignment
- Scope dan visibility identifier
- Penggunaan array dan parameter fungsi

**File terkait:** `symbol_table.py`, `type_checker.py`, `ast_nodes.py`

**Main Entry Point:** `compiler.py` - mengintegrasikan ketiga tahap di atas.

---

## Requirements

* **Python 3.7+**
* File aturan DFA dalam format JSON (`dfa_rules.json`)

---

## Struktur File

```
NTT-Tubes-IF2224/
├── src/
│   ├── compiler.py         # Main entry point
│   ├── lexer.py           # Lexical analyzer (DFA-based)
│   ├── dfa_load.py        # DFA configuration loader
│   ├── token.py           # Token class definition
│   ├── parser.py          # Syntax analyzer (Recursive Descent)
│   ├── ast_nodes.py       # AST node classes
│   ├── symbol_table.py    # Symbol table implementation
│   └── type_checker.py    # Semantic analyzer (Type Checker)
├── test/                  # Test cases
│   ├── milestone1/        # Lexical analysis tests
│   ├── milestone2/        # Syntax analysis tests
│   └── milestone3/        # Semantic analysis tests
├── dfa_rules.json         # DFA transition rules
└── README.md
```

---

## Cara Instalasi dan Penggunaan Program

### Instalasi

1.  *Clone* repositori ini:
    git clone https://github.com/fithrarzk/NTT-Tubes-IF2224
2.  Masuk ke direktori repositori:
    cd NTT-Tubes-IF2224

### Penggunaan Program

Program compiler dapat dijalankan dengan command berikut. Ganti `test/sample_program.pas` dengan file Pascal-S yang ingin dikompilasi.

#### Untuk Mac/Linux
```bash
python3 -m src.compiler test/sample_program.pas
```

#### Untuk Windows
```bash
python -m src.compiler test/sample_program.pas
```

#### Output Program
Program akan menampilkan:
1. **Token list** - Hasil lexical analysis
2. **Parse result** - Hasil syntax analysis (Milestone 2) atau **Abstract Syntax Tree (AST)** (Milestone 3)
3. **Symbol Table** - Isi tab, btab, dan atab (Milestone 3)
4. **Semantic Analysis Result** - Informasi error semantik (jika ada) atau "Analisis semantik berhasil!" (Milestone 3)

#### Contoh File Test
- `test/milestone1/` - Test untuk lexical analysis
- `test/milestone2/` - Test untuk syntax analysis  
- `test/milestone3/` - Test untuk semantic analysis (scoping, array, error detection)

### Pembagian Tugas (Milestone 3)

| NIM | Nama | Pembagian Tugas |
| :--- | :--- | :--- |
| 13523047 | Indah Novita Tangdililing | Integrasi, Error Handling |
| 13523049 | Muhammad Fithra Rizki | Symbol Table |
| 13523053 | Sakti Bimasena | Type Checker |
| 13523055 | Muhammad Timur Kanigara | Base & AST Nodes |
| 13523113 | Kefas Kurnia Jonathan | AST Builder (ke parser) |
