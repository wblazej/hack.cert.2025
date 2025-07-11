import random
from Crypto.Util.number import getPrime


def main():
    flag = open("flag.txt", "rb").read()
    size = len(flag)
    bits = 2048
    p = getPrime(bits // 4)
    q = getPrime(bits // 4)
    n = p * q
    coeffs = [random.randint(2 ** (bits - 1), 2 ** bits) for _ in range(size)]
    res = [flag[i] * coeffs[i] for i in range(size)]
    result = sum(res) % n
    print(n)
    print(coeffs)
    print(result)


main()