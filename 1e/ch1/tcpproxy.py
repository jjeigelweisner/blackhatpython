#!/bin/env python2

import sys
import socket
import threading

def server_loop(local_host,local_port,
                remote_host,remote_port,
                receive_first):

  server = socket.socket(socket.AF_INET,
                         socket.SOCK_STREAM)
                         
  try:
    server.bind((local_host,local_port))
  except:
    print("[!!] Failed to listen on %s:%d" %
          (local_host,local_port))
    print("[!!] Check for other listening " +
          "sockets or correct permissions.")
    sys.exit(0)
    
  print("[*] Listening on %s:%d" %
        (local_host,local_port))
  
  server.listen(5)
  
  while True:
    client_socket, addr = server.accept()
    
    # Print out the local connection information
    print("[==>] Received incoming connection "+
          "from %s:%d" % (addr[0],addr[1]))
    
    # Start a thread to talk to the remote host
    proxy_thread = threading.Thread(
        target=proxy_handler,
        args=(client_socket,
              remote_host,remote_port,
              receive_first))
              
    proxy_thread.start()

def proxy_handler(client_socket,remote_host,
                  remote_port,receive_first):
  # Connect to the remote host
  remote_socket = socket.socket(socket.AF_INET,
                  socket.SOCK_STREAM)
  remote_socket.connect((remote_host,remote_port))
  
  # Receive data from the remote end if necessary
  if receive_first:
    remote_buffer = receive_from(remote_socket)
    hexdump(remote_buffer)
    
    # Send it to our response handler
    remote_buffer = response_handler(
                    remote_buffer)
                    
    # If we have data to send to our
    # local client, send it
    if len(remote_buffer):
      print("[<==] Sending %d bytes to localhost."
            % len(remote_buffer))
      client_socket.send(remote_buffer)
      
  # Now let's loop and read from local,
  # send to remote, send to local.
  # Rinse, wash, repeat.
  while True:
    # Read from local host
    local_buffer = receive_from(client_socket)
    
    if len(local_buffer):
      print("[==>] Received %d bytes from "+
            "localhost." % len(local_buffer))
      hexdump(local_buffer)
      
      # Send it to our request handler
      local_buffer = request_handler(local_buffer)
      
      # Send off the data to the remote host
      remote_socket.send(local_buffer)
      print("[==>] Sent to remote.")
      
    # Receive back the response
    remote_buffer = receive_from(remote_socket)
    
    if len(remote_buffer):
      print("[<==] Received %d bytes from "+
            "remote." % len(remote_buffer))
      hexdump(remote_buffer)
      
      # Send to our response handler
      remote_buffer = response_handler(
                      remote_buffer)
      
      # Send the response to the local socket
      client_socket.send(remote_buffer)
      
      print("[<==] Sent to localhost.")
   
    # If no more data on either side,
    # close the connection
    if not len(local_buffer) or \
       not len(remote_buffer):
      client_socket.close()
      remote_socket.close()
      print("[*] No more data. Closing "+
            "connections.")
      break

# Taken from BLACK HAT PYTHON 1E
def hexdump(src,length=16):
  result = []
  digits = 4 if isinstance(src, unicode) else 2
  
  for i in xrange(0, len(src), length):
    s = src[i:i+length]
    hexa = b' '.join(["%0*X" % (digits,
           ord(x)) for x in s])
    text = b' '.join([x if 0x20 <= ord(x) <
           0x7F else b'.' for x in s])
    result.append(b"%04X  %-*s  %s" %
           (i, length*(digits + 1), hexa, text))  

def receive_from(connection):
  buffer = ""
  
  # We set a 2 second timeout; depending on
  # your target, this may need to be adjusted
  connection.settimeout(2)
  
  try:
    # Keep reading into the buffer until
    # there's no more data
    # or we time out
    while True:
      data = connection.recv(4096)
      
      if not data:
        break
      
      buffer += data
  except:
    pass
    
  return buffer
  
# Modify any requests destined for
# the remote host
def request_handler(buffer):
  # (Perform packet modification)
  return buffer

# Modify any responses destined for
# the local host
def response_handler(buffer):
  # (Perform packet modification)
  return buffer

def main():
  # No fancy command-line parsing here
  if len(sys.argv[1:]) != 5:
    print("Usage: ./proxy.py [localhost] " +
          "[localport] [remotehost] " +
          "[remoteport] [recv_first]")
    print("Example: ./proxy.py 127.0.0.1 " +
          "9000 10.12.132.1 9000 True")
    sys.exit(0)
  
  # Setup local listening parameters
  local_host = sys.argv[1]
  local_port = int(sys.argv[2])
  
  # Setup remote target
  remote_host = sys.argv[3]
  remote_port = int(sys.argv[4])
  
  # This tells our proxy to connect and receive
  # data before sending to the remote host
  receive_first = sys.argv[5]
  
  if "True" in receive_first:
    receive_first = True
  else:
    receive_first = False
    
  #Now spin up our listening socket
  server_loop(local_host,local_port,
              remote_host,remote_port,
              receive_first)
              
main()
