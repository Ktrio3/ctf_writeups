from pwn import *
import re

# You'll want to run this script on the server if your network is slow


def get_coins(r):
    # We want to find the number of coins and number of guesses
    regex = r"N=(\d*) C=(\d*)"
    match = r.recvline_regex(regex, exact=False, keepends=False, timeout=pwnlib.timeout.Timeout.default)
    match = re.findall(r"\d+", match)
    return int(match[0]), int(match[1])


r = remote('pwnable.kr', 9007)
get_coins(r)
# Note that we ignore the above time, as that is from the example

num_wins = 0

# Setup like binary search
while(num_wins < 100):
    num_coins, num_guess = get_coins(r)

    bottom = 0
    top = num_coins
    while num_guess > -1:
        mid = (top + bottom) / 2
        send = ""

        # Test if in range bottom to mid
        if bottom != mid:
            for i in range(bottom, mid):
                send = send + str(i) + " "
        else:
            send = str(bottom)

        r.sendline(send)
        scale_result = r.recvline()

        if scale_result.find("Correct!") > -1:
            num_wins = num_wins + 1
            print scale_result
            # print "Won number: " + str(num_wins)
            break  # Go to next challenge
        elif scale_result.find("format error") > -1:
            print send
            exit()
        scale_result = int(scale_result)  # If not correct, weight of coins

        if scale_result != (mid - bottom) * 10:
            # The counterfeit is located in bottom half
            top = mid
        else:
            bottom = mid
        num_guess = num_guess - 1

print r.recvall()  # Challenge finished, get all of the remaining info
