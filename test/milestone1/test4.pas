program TestOperators;
var
  a, b, c: integer;
begin
  a := 10;
  b := 20;
  if (a < b) and (a <> b) and (a <= b) then
    c := 1;
end.