program ErrorScope;

variabel
    global : integer;

prosedur CekLokal;
variabel
    lokal : integer;
mulai
    lokal := 99;
selesai;

mulai
    global := 1;
    lokal := 5; 
selesai.