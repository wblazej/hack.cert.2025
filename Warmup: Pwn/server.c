#include <stdio.h>
#include <stdlib.h>

void win(void) {
    puts("how did you get here?");
    system("/bin/sh");
}

void func(void) {
    char buf[16];
    scanf("%s", buf);
}

int main(void) {
    func();
    return 0;
}

