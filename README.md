# NTT-Tubes-IF2224

### Identitas Kelompok
### Deskripsi Program
How to run:
`python3 -m src.compiler test/sample_program.pas`
### Requirements
### Cara Instalasi dan Penggunaan Program
### Pembagian Tugas

# NTT-Tubes-IF2224: LEXICAL ANALYSIS

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
`python3 -m src.compiler test/sample_program.pas`

