from pwn import *
import re

r = remote("pwn.ctf.rocks", 6666)

r.readuntil("#>")

r.sendline("1")

magic_reg = r"\[.*\]"
magic_filter = re.compile(magic_reg)

lightning = "6C696768746E696E6720626F6C7421"
allmagic = ""

try:
    while True:
        magic = r.readuntil("#>")

        magic = magic_filter.findall(magic)[0]

        magic = magic[1:]  # Cut off [
        magic = magic[0:-1]  # Cut off ]

        allmagic = allmagic + magic
        place = magic.find(lightning)
        if place is not -1:
            print hex(int(magic))

        r.sendline("2")
except EOFError:
    r = remote("pwn.ctf.rocks", 6666)  # Finished reading, reopen

place = allmagic.find(lightning)
if place is not -1:
    location = place + len(lightning)
    print allmagic[location:location + 10]
