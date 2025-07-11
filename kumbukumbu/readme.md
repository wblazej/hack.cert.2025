# kumbukumbu

We got `index.html` that includes parts of the flag encrypted using RSA, but some prime factors are missing. We can search for them using [factordb.com](https://factordb.com/). Once we have all of the prime factors, we can decrypt the flag:
```py
def extended_gcd(a, b):
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y


def mod_inverse(a, m):
    gcd, x, _ = extended_gcd(a, m)
    if gcd != 1:
        return None

    return (x % m + m) % m


def mod_exp(base, exp, mod):
    if mod == 1:
        return 0
    result = 1
    base %= mod
    while exp > 0:
        if exp % 2 == 1:
            result = (result * base) % mod
        exp >>= 1
        base = (base * base) % mod
    return result


def bigint_to_string(n):
    result = ""
    while n > 0:
        char_code = n % 256
        result = chr(char_code) + result
        n //= 256
    return result


def rsa_decrypt(ciphertext, p, q):
    n = p * q
    phi = (p - 1) * (q - 1)
    e = 65537

    d = mod_inverse(e, phi)

    plaintext = mod_exp(ciphertext, d, n)
    return bigint_to_string(plaintext)


primes = [
    1038934092753097872730253139059,
    1215072113218197541320209640371,
    993312580651766761514801353103,
    1142600241573404407687535573629,
    646707326780153459647011532987,
    813122100173370069804649439983,
    693661003419668078345820408199,
    1253977927505847682354254592843,
    1167170536952850475909418174911,
    885099533904372795874859687719,
    778021292426438436606425112727,
    1055301397731143498286103730113,
    1033646404229761438304319507287,
    1255561944672568469862862185019,
    1262714843670806964782879865877,
    892852023919058398648656968671,
]

inputs = [
    {'id': 1033062098243884481013064396504107415412074063278620380618009,
        'c': 538634309079148116363912301816926031930258573110799122862941},
    {'id': 821046957362211211370998260729299679185917409099391209448151,
        'c': 562733309494608716994364770937828277740523146074677621141932},
    {'id': 1262379843575937484146622348873014780040324339468876243350889,
        'c': 319243791255303502020259161971610515049913374771288695699737},
    {'id': 1297807089398527074605667633852686491395225225926566312733453,
        'c': 941629393855667943649547190044646980315269461850095508227115},
    {'id': 1134959194610610450739805279442633776492217914200656484120787,
        'c': 914355749731699186791425204706414002614646261411469947941828},
    {'id': 1127417503804117426722865115226225402522827590523333870939467,
        'c': 558030107305255463640139626217118512514526900834839072384186},
    {'id': 525852019748984313817496717882753277681519784980531881219221,
        'c': 251738364156397018723696894127984058119319062121032554046180},
    {'id': 869835587459822098831531231565804817101360778375336803919757,
        'c': 774165720938595325818024236038187794673577169187146034055752}
]

decrypted_parts_map = {}

for inp in inputs:
    n = inp['id']
    c = inp['c']

    found = False
    for i in range(len(primes)):
        for j in range(i + 1, len(primes)):
            if primes[i] * primes[j] == n:
                p = primes[i]
                q = primes[j]

                decrypted = rsa_decrypt(c, p, q)
                decrypted_parts_map[n] = decrypted
                found = True
                break
        if found:
            break


flag = "".join([decrypted_parts_map.get(inp['id'], "") for inp in inputs])
print(flag)
# ecsc25{C@nT_eSc@p3_mY_r$A_eveRywHeRe_I_l00k_l_s33_it$_Prim3$:((}
```