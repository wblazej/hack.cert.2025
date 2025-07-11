code = ''
while True:
    code_chunk = input()
    code += code_chunk+"\n"
    if '# end' in code_chunk:
        break
exec(code)