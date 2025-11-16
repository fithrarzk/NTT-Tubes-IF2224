program ErrorMissingSyntax;

variabel
    x, y, z : integer;
    hasil : real;

prosedur hitung(a : integer);
mulai
    x := a * 2
selesai;

mulai
    x := 10;
    y := 20;
    
    jika x > y
        z := x
    selain_itu
        z := y;
    
    selama z > 0
        z := z - 1;
    
    writeln('X = ', x);
    writeln('Y = ', y);
    writeln('Z = ', z);
    
selesai.
