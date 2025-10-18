program RangeArray;
var
  i: integer;
  arr: array[5..10] of integer;
begin
  for i := 5 to 10 do
    arr[i] := i * 2;

  for i := 5 to 10 do
    writeln('arr[', i, '] = ', arr[i]);
end.