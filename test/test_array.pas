program ArrayTest;

variabel
  i: integer;
  arr: larik[1..5] dari integer;

mulai
  arr[1] := 10;
  arr[2] := 20;
  i := arr[1] + arr[2];
  writeln('Sum = ', i);
selesai.
