# Start with a slim and secure Python base image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy the Python application into the container
COPY runner.py .
COPY flag.txt .

# Install socat, a modern and more secure alternative to netcat for this use case
RUN apt-get update && \
    apt-get install -y socat && \
    rm -rf /var/lib/apt/lists/*

# Expose the port the server will listen on
EXPOSE 1337

# Command to run the socat server, which will execute the Python script for each connection
# socat will listen on TCP port 1337 and fork a new process for each connection,
# executing the python script. 'reuseaddr' allows immediate restart of the server.
CMD ["socat", "TCP-LISTEN:1337,fork,reuseaddr", "EXEC:python3 runner.py"]