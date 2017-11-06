# Unlink

This challenge is nice enough to give us the source code for the program.
Upon examining it, we see comments that head us in the right direction. This is a straight forward challenge; exploit the heap!

I wrote the above as I was solving the challenge; this was not as straight forward as I thought! With the name and code given, I assumed it was simply place some shellcode in the heap, and point EIP at it using the unlink. Running checksec on this, the program has NX enabled, totally squashing this idea. We also can't just overwrite the stored eip with the address of the shell function; the unlink function would try to overwrite this address + 4, which would not only break the function, but is located in non-writeable memory! Indeed, this "straight forward" actually had a much more elegant solution.

## Setup

Taking a look at the source code, we have a handy function called shell, which spawns a shell for us. Having this function makes our goal obvious: call this function!

When we run the program, we see that it prints the address of the pointer to struct A on the stack, and the address of A on the heap. This addresses will be used heavily; we will need them to determine where and what to write.

Running checksec on the program, we see that the program has NX enabled; we will not be able to pass in our own shellcode. We will need to be more clever. As we will see later, ROP is out of the question; the overflow occurs in the heap, not the stack.

## Vulnerability

The vulnerability in this case is in the following two sections of code:

		gets(A->buf);

The vulnerability here is obvious. A string of any size will be read into a buffer on the heap that is only 8 bytes long.

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

In this case, FD is our where we want to write. The BK will be our what. However, there is a catch!

		BK->fd=FD;

The above line will effectively punch a hole into wherever we want to write; it will write our where directly into our what! 

For example, assuming we were jumping to shellcode on the heap, the following will occur:

			ssssaaaasssss

The aaaa is the hole, the address of the where, and s is our shellcode. This is a minor inconvencience in shellcode; we can just jump over the hole. However, NX is enabled; we aren't going to be using shellcode.

## The What and Where

Knowing we can write to any arbitrary address is good, but now we need to know what we are going to write, and where. We already ruled out shellcode. The next idea is to write the address of the shell function into the saved eip; however, we run into the same snag we would have with shellcode. The unlink function would write the address of saved eip into the shell function. Not only is that memory not writeable, it would also break the function. Let's take a deeper look into main.

In main, before leave and ret, we see this:

		0x080485ff <+208>:	mov    ecx,DWORD PTR [ebp-0x4]
		0x08048602 <+211>:	leave  
		0x08048603 <+212>:	lea    esp,[ecx-0x4]
		0x08048606 <+215>:	ret  

This code is what we will use to gain control of eip; let's take a look more closely at what happens.

1. Whatever is contained in the address ebp-0x4 is moved into ecx.
2. Leave is called. (EBP is moved into esp, and the stored ebp is popped into ebp. Unimportant for us)
3. ecx - 0x4 is moved into esp.
4. Ret is called. Whatever esp is pointing at (in other words, the contents of the address contained at ecx-0x4) is moved into esp.

We can use this to our advantage; if we can overwrite ebp-0x4 in the main stack, we can point it somewhere. If that place it's pointing contains the address of shell, EIP will execute shell!

## The exploit

So to exploit this vulnerability, we need the do the following:

1. Calculate the distance from the address of A on the stack (in main) to ebp-0x4
2. Calculate the address of ebp-0x4 by adding the observed value of A to the distance
3. Calculate the distance from the buffer in A on the heap to B
4. Calculate the address  of the buffer in B by adding the distance from A to B to the observed heap address (+8 for the two pointers)
5. Inside B, have FWD point to the address ebp-0x4
6. Inside B, have BCK point to the beginning of the buffer in B
7. Inside the buffer in B, place the address of shell A

Thus, esp will end up pointing the the buffer in B, and the contents of buffer B, the address of shell, will be loaded into eip.

		... | FD A | BK A | BUF A(AAAA)          | BUF A(AAAA)                       | ... 
		... | FD B | BK B | BUF B(Addr of shell) | BUF B(OVERWRITTEN BY BK->fd = FD) | ...

### Distance from Address A to ebp -0x4

This is fairly easy to do; simply run the program in GDB, and break at 0x080485ff (mov ecv, DWORD PTR\[ebp-0x4\])

		b *0x080485ff
			...
		r
			here is stack address leak: 0xffcf7e64
			here is heap address leak: 0x8d30410
			now that you have leaks, get shell!
		AAAA
			...
		i r ebp
			ebp		0xffcf7e78	0xffcf7e78
		x/20x $esp
			0xffcf7e60:	0x00000001	0x08d30410	0x08d30440	0x08d30428
			0xffcf7e70:	0xf773c3dc	0xffcf7e90	0x00000000	0xf75a2637
			0xffcf7e80:	0xf773c000	0xf773c000	0x00000000	0xf75a2637
			0xffcf7e90:	0x00000001	0xffcf7f24	0xffcf7f2c	0x00000000
			0xffcf7ea0:	0x00000000	0x00000000	0xf773c000	0xf778ec04

Using the above, we can find the distance from A to ebp-0x4. We know the value of the address A, since it was leaked. By printing ebp at the breakpoint, we know that as well. Thus, the distance is (0xffcf7e78 - 4) - 0xffcf7e64.

In this case, the address of struct A is 0x08d30410 and ebp-0x4 contains 0xffcf7e90.

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

This chunk of heap contains the structure B. We can see the fd and bk pointers (with the addresses of C and A, respectively). The last 8 bytes are the buffer, which contains no data. (Also of note, we can see the heap meta data, the first 8 bytes shown, 0x00000000 and 0x00000019)

## Exploit!

With the above information, we can exploit the program!

A program to exploit the vulnerability can be found in sol.py. This file will connect to the remote host, exploit the program, and return an interactive shell.





