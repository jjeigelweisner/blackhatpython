#!/bin/env python3

import socket

target_host = "www.google.com"
target_port = 80

client = socket.socket(socket.AF_INET,
                       socket.SOCK_STREAM)

client.connect((target_host, target_port))

client.send(("GET / HTTP/1.1\r\nHost: www.google.com"+
            "\r\n\r\n").encode("UTF-8"))

response = client.recv(4096)

print(response.decode("UTF-8"))
