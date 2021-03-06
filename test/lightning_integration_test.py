#!/usr/bin/env python

from subprocess import Popen
from subprocess import PIPE
import sys

print("\nSTART Lightning integration tests\n")

# We start off with the assumption that the test will succeed
ec = 0

# Test echoing using httpie
# Try a background fork/thread
server_process = Popen(['./lightning', 'simple_config'])

# Spawn a shell process to act as hanging http request
# This tests multithreading
telnet_request_command = "telnet localhost 8080"
telnet_request_proc = Popen(telnet_request_command, stdout=PIPE, shell=True)

# TODO: Have intermediate logging throughout
# TODO: Use Python unit test frameworks + logging libraries
print('DEBUG: Lightning server started!')

# as the telnet is hanging, we will perform an echo request, which should still be
# handled by a separate handler in a new thread; it will still succeed and return
# a response instantly.

expected_response = b"""GET /echo HTTP/1.1\r\nHost: localhost:8080\r\n\
Accept-Encoding: gzip, deflate, compress\r\n\
Accept: */*\r\nUser-Agent: HTTPie/0.8.0\r\n\r\n"""
actual_response = Popen(['http', 'localhost:8080/echo'], stdout=PIPE)

if (actual_response.communicate()[0].decode() != expected_response):
    print('FAILED: httpie received a non-matching echo response')
    ec = 1;
else:
    print('SUCCESS: HTTPie request echo; Multithreading successful!')

# Test proxy server
print('DEBUG: Creating proxy server!')
proxy_server_process = Popen(['./lightning', 'proxy_config'])

expected_proxy_response = b'<!DOCTYPE html><html><head></head><body><h1>Hello World!</h1></body></html>'
actual_proxy_response = Popen(['http', 'localhost:3030/reverse_proxy/static/index.html'], stdout=PIPE)

if (actual_proxy_response.communicate()[0].decode() != expected_proxy_response):
    print('FAILED: proxy server received a non-matching proxy response')
    ec = 1;
else:
  print('SUCCESS: Received expected reverse proxy response!')

# Terminate the server
server_process.kill()
proxy_server_process.kill()

# Return 0 if the test succeeded or some other value on failure
if ec == 0:
    sys.stdout.write("Finished Integration Test. ALL TESTS PASSED!\n")
    sys.exit(0)
else:
    sys.stdout.write("INTEGRATION TEST FAILED\n")
    sys.exit(ec)
