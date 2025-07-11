import random
import socket
from flask import Flask, request, abort, jsonify, render_template
from typing import List, Tuple

app = Flask(__name__)

MAZE = List[List[str]]
size = 100
clear = 15
sandbox_host = "localhost"
sandbox_port = 1337


def nc(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    return s


def safe_run(script: str, maze: MAZE) -> Tuple[MAZE, List[int]]:
    script = build_script(script, maze)
    s = nc(sandbox_host, sandbox_port)
    s.sendall(script.encode())
    result = b''
    while True:
        output_chunk = s.recv(1000)
        result += output_chunk
        if b']' in output_chunk or not output_chunk:
            s.close()
            break
    result = result.replace(b"[", b"").replace(b"]", b"").decode()
    result = [int(x) for x in result.split(",") if 0 <= int(x) < 4][:size]
    return maze, result


def generate_maze() -> MAZE:
    maze = [['.' for _ in range(size)] for _ in range(size)]
    for i in range(size):
        for j in range(size):
            if size // 2 - clear < i < size // 2 + clear and size // 2 - clear < j < size // 2 + clear:
                pass
            else:
                if random.getrandbits(3) > 3:
                    maze[i][j] = '#'
    return maze


def build_script(script: str, maze: MAZE) -> str:
    script = '\n'.join(["    " + line for line in script.splitlines()])
    template = f"""
def make_move(up:str,down:str,left:str,right:str) -> int:
{script}
    pass
def main():
    maze = {maze}
    results = []
    pos_x = len(maze)//2
    pos_y = len(maze[0])//2
    for _ in range(len(maze)):
        left = maze[pos_x-1][pos_y]
        right = maze[pos_x+1][pos_y]
        up = maze[pos_x][pos_y-1]
        down = maze[pos_x][pos_y+1]
        step = make_move(up,down,left,right)
        if (step == 0 and left=='.'):
            pos_x-=1
            results.append(step)
        elif (step == 1 and right=='.'):
            pos_x+=1
            results.append(step)
        elif (step == 2 and up=='.'):
            pos_y-=1
            results.append(step)
        elif (step == 3 and down=='.'):
            pos_y+=1
            results.append(step)
    print(results)
main()
# end
"""
    return template


@app.route('/', methods=['GET'])
def visualize():
    return render_template("view.html")


@app.route('/submit', methods=['POST'])
def run():
    code = request.json['code']
    if len(code) < 1000:
        maze, moves = safe_run(code, generate_maze())
        return jsonify({'maze': maze, 'moves': moves, 'pos_x': size // 2, 'pos_y': size // 2})
    else:
        abort(403)


if __name__ == '__main__':
    app.run(port=5001)
