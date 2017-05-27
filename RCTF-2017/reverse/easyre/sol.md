This challenge is an exercise in scrutiny. The author attempts to distract
you away from the solution.

When you first run the executable, it appears nothing has happened. Executing the program with strace gives us:



	unlink("AAAAAAAAAU1NMDPAQOE")           = -1 ENOENT (No such file or directory)
	open("AAAAAAAAAU1NMDPAQOE", O_WRONLY|O_CREAT|O_EXCL, 0700) = 4
	ftruncate(4, 7540)                      = 0
	mmap(NULL, 12288, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_ANONYMOUS, -1, 0) = 0xf77b1000
	read(3, "t\35\0\0\220\n\0\0", 8)        = 8
	read(3, "\177?d\371\177ELF\1\0\2\0\3\0\r@\205\4\377o\263\335\0104\7p\21\27\v \0\10"..., 2704) = 2704
	write(4, "\177ELF\1\1\1\0\0\0\0\0\0\0\0\0\2\0\3\0\1\0\0\0@\205\4\0104\0\0\0"..., 7540) = 7540
	read(3, "\0\0\0\0UPX!", 8)              = 8
	unlink("AAAAAAAAAU1NMDPAQOE")

We see this attempts to delete a file, creates a file, writes to it, and then deletes it again!

Two more things worth noticing by executing this again:
1. The filename is random.
2. The data beung written to a file is an ELF executable!

To get a hold of this file, I simply booted up IDA and placed a breakpoint on the line right after the write syscall. Once the executable gets to this point, simply terminate the program! Voila! One new executable.

The file can be now be found in your pwd. It may not be executable, so chmod +x it.

Running this executable, we see:

	OMG!!!! I forgot kid's id
	Ready to exit

This is a bit deceiving; our program is still asking for stdin. It did not exit. If we take a look in IDA, we see that fork is called in main. The child process just prints the above, while the parent continues through the rest of the program.

Looking through IDA, we see a scanf, with a "%d" param. If the number entered does not match a number on the stack, the program jumps to the bottom and exits.

The number, however, is random; to find the value, simply place a breakpoint in IDA, then continue execution and enter the number. The number to compare is at esp+20h.

Once that is finished, we are taken to the LOL function. Viewing this in IDA, we see there is another branch:

	mov     [ebp+var_D], al
	mov     [ebp+var_C], 0
	cmp     [ebp+var_C], 1

Since ebp+var_C is zeroed out right before the cmp, the following jnz will always be taken! If we let execution continue, we just see flag_is_not_here

When I first saw this, I thought I had missed something in the original executable.

However, the flag is simply in the other branching path!

Since we can never get there, we will use our breakpoints again; simply set your breakpoint somewhere in the lol function after the variables have been set up in the beginning.

We want to view the string being passed to the printf; this will be the second arguement.

	lea     edx, [ebp+var_13]
	mov     [esp+4], edx
	mov     [esp], eax
	call    _printf

Thus, we want to see the string at ebp + var_13. In the beginning of the function, we see that var_13 is always set to be -13h. Once you have placed your breakpoint, simply examine ebp - 13h, and voila!

	"rhelheg"

While this doesn't look like a flag, wrap it up inside RCTF{}, RCTF{rhelheg}, and you just finished easy_re. 
