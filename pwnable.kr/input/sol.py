from pwn import *
from subprocess import Popen, PIPE, STDOUT
import sys
import time
import os
import pipes

if 't' in sys.argv:
    test = True
else:
    test = False

# First up: argv, stage 1

# Nice and easy. First create an array of 100 strings
# Note that arg 0 is NOT the filename, as the program name is not available to
#   the program when using process

argv = ["file_name"]

for i in range(1, 100):
    argv.append(str(i))

# Place correct string in location 'A' and 'B'
argv[ord('A')] = "\x00"
argv[ord('B')] = "\x20\x0a\x0d"

# print " ".join(argv)

if test:
    print "Argv has length: " + str(len(argv))
    print "Argv['A'] is 0x" + argv[ord('A')].encode('hex')
    print "Argv['B'] is 0x" + argv[ord('B')].encode('hex')
    print

# Now to setup stdin and stderr, stage 2
stdin = "\x00\x0a\x00\xff"  # stdin is nice and easy...

# stderr will require a pipe, which we will do as a file
with open('magic', 'w+') as f:
    f.seek(0)
    f.write("\x00\x0a\x02\xff")
    f.truncate()

'''
p1 = process(argv=['python', 'stderr.py'], stdout=PIPE)
time.sleep(.1)

# Run the input program!
if not test:
    input = process(executable='/home/input2/input', argv=argv, stderr=p1.stdout)
else:
    input = process(executable='./input', argv=argv, stderr=p1.stdout)
input.sendline(stdin)

print input.recvall()
'''

# Now to setup ENV, stage 3
env = {"\xde\xad\xbe\xef": "\xca\xfe\xba\xbe"}

# Run the input program!
if not test:
    executable = '/home/input2/input'
else:
    executable = './input'

# Now the file, stage 4
with open('\x0a', 'w+') as f:
    f.seek(0)
    f.write("\x00\x00\x00\x00")
    f.truncate()

# Now for networking, stage 5
# Note that the port number comes from argv['C'], so we should add that
argv[ord('C')] = "22224"

input = process(executable=executable, argv=argv, env=env, stderr=open('magic', 'r+'))
input.sendline(stdin)

time.sleep(1)  # Give some time for the socket to setup
# Now lets do our networking
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Bind the socket to the port
server_address = ('localhost', 22224)
sock.connect(server_address)
sock.send("\xde\xad\xbe\xef")

print input.recvall()
