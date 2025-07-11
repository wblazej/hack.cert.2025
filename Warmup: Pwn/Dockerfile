FROM ubuntu:22.04
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC apt-get install -y \
        autoconf bison flex gcc g++ libprotobuf-dev libnl-route-3-dev \
        libtool make pkg-config protobuf-compiler git clisp && \
    rm -rf /var/lib/apt/lists/*
RUN git clone https://github.com/google/nsjail && \
    cd /nsjail && make && mv nsjail /bin/nsjail

WORKDIR /app/

COPY sandbox.cfg /app
COPY flag.txt /app
COPY server.c /app
RUN gcc -z execstack -fno-stack-protector -fno-pie -no-pie -o /app/server /app/server.c

CMD [ "nsjail", "--config", "/app/sandbox.cfg" ]

