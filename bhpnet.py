#!/bin/env python2

import sys
import socket
import getopt
import threading
import subprocess

# Define some global variables
listen              = False
command             = False
upload              = False
execute             = ""
target              = ""
upload_destination  = ""
port                = 0

def usage():
  print "BHP Net Tool"
  print "Usage: bhpnet.py -t target_host " +
        "-p port"
  print "-l --listen  listen on [host]:port]\n"+
        "             for incoming connections"
  print "-e --execute=file_to_run\n"+
        "             execute the given file\n"+
        "             upon receiving a connection"
  print "-c --command initialize a command shell"
  print "-u --upload=destination\n"+
        "             upon receiving connection"+
        "\n             upload a file and write"+
        "\n             to [desination]\n"
  print "Examples:"
  
