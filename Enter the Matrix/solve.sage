import ast

with open('output.txt', 'r') as f:
    n = int(f.readline().strip())
    coeffs = ast.literal_eval(f.readline().strip())
    result = int(f.readline().strip())

size = len(coeffs)

L = matrix(ZZ, size + 2, size + 2)

for i in range(size + 1):
    L[i, i] = 1

for i in range(size):
    L[i, size + 1] = coeffs[i]

L[size, size + 1] = -result
L[size + 1, size + 1] = n

reduced_basis = L.LLL()

for row in reduced_basis:
    if row[size + 1] == 0:
        k = row[size]
        if abs(k) == 1:
            flag_bytes = [c / k for c in row[:size]]

            if all(c.is_integer() and 32 <= c <= 126 for c in flag_bytes):
                flag = "".join(chr(int(c)) for c in flag_bytes)
                print(flag)
