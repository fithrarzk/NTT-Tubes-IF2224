program TestStrings;
begin
  writeln('It''s a string literal.');
  writeln('This string has ''two'' escaped quotes.');
  writeln('''');
end.


PROGRAM TestSpacing;
VAR
  X:INTEGER;
BEGIN
  IF(X=1)THEN
    X:=2;
  (* Spasi normal untuk perbandingan *)
  if (x = 1) then
    x := 2;
END.


program TestError;
var
  x: integer;
begin
  x := 10;

  x := x $ 5;
end.



program TestOperators;
var
  a, b, c: integer;
begin
  a := 10;
  b := 20;
  if (a < b) and (a <> b) and (a <= b) then
    c := 1;
end.

program TestRangeContext;
var
  validRange: array[1..10] of integer;
  x, y: integer;
begin
  x := 5..10; 
end.