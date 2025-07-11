import os
import uuid


def main():
    FLAG = open("flag.txt", 'r').read().encode()
    arg = input("> ")
    blacklist = ['{', '}', ';', '\n']
    if len(arg) > 10 or any([c in arg for c in blacklist]):
        print("Bad input!")
        return
    template = f"""
#include <stdio.h>
#include <string.h>

char* f(){{
    char* flag = "{FLAG}";
    printf("%s",flag);
    return flag;
}}

void g(char* {arg}){{}}

int main(){{
    g(NULL);
    return 0;
}}
"""
    name = "test"
    source = f"{name}.c"
    outfile = f"{name}"
    open(source, 'w').write(template)
    os.system(f"export PATH=$PATH:/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin && gcc {source} -o {outfile}")
    os.system(f"{outfile}")
    os.remove(source)
    os.remove(outfile)


main()