# Unlink

This challenge is nice enough to give us the source code for the program.
Upon examining it, we see comments that head us in the right direction. This is a straightfoward challenge; exploit the heap!

## Setup

When the program is run, it provides the address of A on the stack, and the address of A on the heap. Finding the heap address is the major difficulty with heap exploits, so this will be quite helpful. These two addresses serve help us find the where and the what for writing.

The stack address will help us find where we want to write; we want to take control of EIP, and point it at some code that we control. Using the leaked stack address, we can calculate the distance from A to the return address, and add this distance to the leaked address to find the address of return address.

The heap address will help us find what we want to write into EIP. Our shellcode will be somewhere on the heap since we are writing into the buffer in A. We will use this address to determine where to point our return address.

## Vulnerability

The vulnerability in this case is in the following two sections of code:

		gets(A->buf);

The vulnerability here is obvious. A string of any size will be read into a buffer that is only 8 bytes long.

		void unlink(OBJ* P){
			OBJ* BK;
			OBJ* FD;
			BK=P->bk;
			FD=P->fd;
			FD->bk=BK;
			BK->fd=FD;
		}
		...
		unlink(B);

This is where we get something interesting; if we can overflow the buffer in A into B, we can change the bk and fd pointers contained in B. Thus, in the above unlink function, we can control the values of BK and FD. The following line is the one that allows us to do what we want:

		FD->bk=BK;

In this case, FD is our where we want to write. We will want FD to become the address of the return address. The BK will be our what; this will be the address of our shellcode in the heap. However, there is a catch!

		BK->fd=FD;

The above line will effectively punch a hole into our shellcode; it will write our where directly into our what! For example, the following will occur:

			ssssaaaasssss

The aaaa is the hole, the address of the return address, and s is our shellcode; we will need to write shellcode that can handle this. The beginning 4 bytes of our shellcode will need to be a jmp instruction that jumps over the hole. Fortunately, we can do this with a short relative jump instruction.

## The exploit

So to exploit this vulnerability, we need the following:

1. The distance from the address of A on the stack to the return address
2. The distance from the buffer in A on the heap to B.
3. The shellcode, including a jump over the hole.

### Address A to return

Opening up gdb, we can put a break point at the retn instruction, and see where esp points. The esp points to the value 0xf756a637 at 0xffa314ec, and we can see the dump of the stack from the address of A to the return address. Thus, the distance from is A to eip is 0xffa314ec - 0xffa314c4 = 0x28

		x/7x 0xffa314c4
		0xffa314c4:	0x093d7410	0x093d7440	0x093d7428	0xf77043dc
		0xffa314d4:	0xffa314f0	0x00000000	0xf756a637

### Buffer to B

I executed the program and entered AAAAAAAA. When we examine the heap at the given address, we see the following:

		x/16x 0x93d7410
		0x93d7410:	0x093d7428	0x00000000	0x41414141	0x41414141
		0x93d7420:	0x00000000	0x00000019	0x093d7440	0x093d7410
		0x93d7430:	0x00000000	0x00000000	0x00000000	0x00000019
		0x93d7440:	0x00000000	0x093d7428	0x00000000	0x00000000

Here we can see each of the structures in our linked list: A,B,C

		0x93d7410:	0x093d7428	0x00000000	0x41414141	0x41414141

A is the easiest to recognize because of our strings of A's. The first 4 bytes are the fd pointer, which we can see points to the beginning of the B structure. The bk pointer, the next 4 bytes, is all 0's as there is nothing before A.

		0x93d7420:	0x00000000	0x00000019	0x093d7440	0x093d7410
		0x93d7430:	0x00000000	0x00000000

This chunk of heap contains the structure B. We can see the fd and bk pointers (with the addresses of C and A, respectively). The last 8 bytes are the buffer, which contains no data. (Also of note, we can see the heap meta data, the first 8 bytes shown. It is not necessary to understand it for this challenge, but if we were exploiting the heap unlink function, it would be essential.)

### The shellcode

We actually don't need to write shellcode! There is a function provided, shell, that can call the shell for us. We simply need to call this function.


## Exploit!

A program to exploit the vulnerability can be found in sol.py. This file will connect to the remote host, exploit the program, and return an interactive shell.





