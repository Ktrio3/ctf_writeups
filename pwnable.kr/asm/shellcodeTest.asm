BITS 64

jmp short one

two:
  pop r10

  ; 1 -> write(0, r10, rdx)
  ; rdx is value returned from read
  mov rdx, 30
  mov rax, 1
  mov rdi, 0
  mov rsi, r10
  syscall

  ; 60 -> exit(0)
  mov rax, 60
  mov rdi, 0
  syscall

one:
  call two
  db "this_is_pwnable.kr_flag_file_please_read_this_file.sorry_the_file_name_is_very_loooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo0000000000000000000000000ooooooooooooooooooooooo000000000000o0o0o0o0o0o0ong"
