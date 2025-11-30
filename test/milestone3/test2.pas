program TesTabelLarik;

variabel
    nilai_ujian : larik[1..10] dari integer;
    saldo : larik[0..5] dari integer;
    i : integer;

mulai
    nilai_ujian[1] := 100;
    nilai_ujian[10] := 90;

    saldo[0] := 5000;
    saldo[5] := 1000;
    
    writeln('Nilai pertama: ', nilai_ujian[1]);
    writeln('Saldo akhir: ', saldo[5]);
selesai.