#!/bin/env python2

import socket
import paramiko
import threading
import sys

# Using the key from the Paramiko demo files
host_key = paramiko.RSAKey(
           filename='test_rsa.key')

class Server (paramiko.ServerInterface):
  def __init__(self):
    self.event = threading.Event()
  def check_channel_request(self,kind,chanid):
    if kind == 'session':
      return paramiko.OPEN_SUCCEEDED
    return paramiko.
           OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED
  def check_auth_password(self,username,password):
    if (username == 'mike') and
       (password == 'lovespython'):
      return paramiko.AUTH_SUCCESSFUL
    return paramiko.AUTH_FAILED
    
server = sys.argv[1]
ssh_port = int(sys.argv[2])

