program SemanticScope;

variabel
    angka : integer; 

prosedur CekLokal;
variabel
    angka : integer;
mulai
    angka := 100; 
    writeln('Angka Lokal: ', angka);
selesai;

mulai
    angka := 1; 
    CekLokal();  
    writeln('Angka Global: ', angka);
selesai.