# NTT-Tubes-IF2224: LEXICAL ANALYSIS

Lexer sederhana untuk Subset Pascal-S. Konverter teks sumber (.pas) menjadi daftar token menggunakan DFA yang dikonfigurasi lewat JSON.

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

Program ini adalah sebuah **Lexical Analyzer (Lexer)** untuk bahasa pemrograman Pascal-S.
Program ini merupakan implementasi dari tahap pertama *compiler* yang bertugas membaca file kode sumber Pascal-S (`.pas`) dan mengubahnya dari rangkaian karakter mentah menjadi daftar **token** yang bermakna.

Lexer ini diimplementasikan menggunakan **Deterministic Finite Automaton (DFA)**. Aturan transisi DFA (state, input, state selanjutnya) tidak di-*hardcode*, melainkan dibaca dari sebuah file konfigurasi eksternal (`dfa_rules.json`). Program kemudian menyimulasikan DFA ini untuk mengenali *lexeme* dan mengklasifikasikannya ke dalam tipe token yang sesuai (misalnya `KEYWORD`, `IDENTIFIER`, `NUMBER`, dll.).

---

## Requirements

* **Python 3.7+**
* File aturan DFA dalam format JSON (secara default `dfa_rules.json`).

---

## Cara Instalasi dan Penggunaan Program

### Instalasi

1.  *Clone* repositori ini:
    git clone https://github.com/fithrarzk/NTT-Tubes-IF2224
2.  Masuk ke direktori repositori:
    cd NTT-Tubes-IF2224

### Penggunaan Program
Jalankan perintah ini melalui terminal, ganti 'test/sample_program.pas' dengan file yang akan dibaca.

#### Untuk Mac
`python3 -m src.compiler test/sample_program.pas`

#### Untuk Windows
`python -m src.compiler test/sample_program.pas`

### Pembagian Tugas
| Nama | NIM | Pembagian Tugas |
| :--- | :--- | :--- |
| Indah Novita Tangdililing | 13523047 | Membuat DFA Rules, Implementasi dfa_load.py, Melakukan testing, Membuat laporan |
| Muhammad Fithra Rizki | 13523049 | Implementasi lexer.py, Membuat DFA Rules, Melakukan testing, Membuat laporan, Membuat state diagram DFA |
| Sakti Bimasena | 13523053 | Implementasi lexer.py, Membuat DFA Rules, Melakukan testing, Membuat laporan, Membuat state diagram DFA, |
| Muhammad Timur Kanigara | 13523055 | Membuat DFA Rules, Implementasi token.py, Melakukan testing, Membuat laporan |
| Kefas Kurnia Jonathan | 13523113 | Membuat DFA Rules, Implementasi compiler.py, Melakukan testing, Membuat laporan |
