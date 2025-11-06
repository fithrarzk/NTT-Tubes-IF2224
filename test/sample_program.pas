program TestRangeContext;
variabel
  validRange: larik[1..10] dari integer;
  x, y: integer;
fungsi fungsi1 (a,b,c : integer; ab,ac : char): 
  integer;
  variabel
    valid: boolean;
    sum: integer;
  mulai
    sum := a+b;
    jika sum < 7
    maka valid := 1
    selain_itu valid := 0
  selesai;
mulai

selesai.