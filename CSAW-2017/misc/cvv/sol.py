from pwn import *
from random import randint
import re
from luhn import *

# This code is terrible... That's what I get for working at 2 in the morning...

def validate_card(code):
    valid = 1
    #for card_type in card_details:
    #    found_beginning = False
    #    for beginning in card_type[0]:
    #        if card[0:len(str(beginning))] == str(beginning):
    #            found_beginning = True
    #    found_length = False
    #    for length in card_type[1]:
    #        if len(card) == length:
    #            found_length = True

    last_digit = code[-1]

    code_checker = code[::-1]  # Reverse

    # Multiple every other digit, starting at pos 0
    num_list = []
    for count, i in enumerate(code_checker):
        if count % 2 == 1:
            new_num = (int(i) * 2)
            if new_num > 9:
                new_num = new_num - 9

            num_list.append(new_num)
        else:
            num_list.append(int(i))

    sum_list = sum(num_list)

    print sum_list
    print last_digit

    #if "0" == str(sum_list % 10):
    if verify(code):
        print True
        return "1"
    else:
        print False
        return "0"

    #if luhn_checksum(card):  # and found_length and found_beginning:
    #    return "1"
    #else:
    #    return "0"

# Return the "Luhn transform" of a digit.
luhnify = lambda digit: sum(divmod( digit*2, 10 ))

def luhn_checksum( digits ):
    """Return the Luhn checksum of a sequence of digits.
    """
    digits = map( int, digits )
    odds, evens = digits[-2::-2], digits[-1::-2]
    return sum( map(luhnify,odds) + evens ) % 10


def cardLuhnChecksumIsValid(card_number):
    """ checks to make sure that the card passes a luhn mod-10 checksum """

    sum = 0
    num_digits = len(card_number)
    oddeven = num_digits & 1

    for count in range(0, num_digits):
        digit = int(card_number[count])

        if not ((count & 1) ^ oddeven):
            digit = digit * 2
        if digit > 9:
            digit = digit - 9

        sum = sum + digit

    return ((sum % 10) == 0)


r = remote("misc.chal.csaw.io", 8308)

card_details = {"MasterCard": ((51, 52, 53, 54, 55, "2221000-272099"), 16), "Visa": ((4,), 17), "American Express": ((34, 37), 15), "Discover": ((65, 6011, "622126-622925", 644, 645, 646, 647, 648, 649), 16)}

need = r.recv()
print need
need = need[13:-2]
needs_Valid = False

start = 0
setEnd = False

while(True):
    # print need

    try:
        length = card_details[need][1]
        start = str(card_details[need][0][0])
    except KeyError:
        if need[10:13] == "sta":
            start = need[22:]
            length = 13
        else:
            start = "51"
            length = 12
            group = re.findall('\d+', need)
            # print group
            end = group[0]
            setEnd = True

            print need[0:5]
            if need[0:5] == "w if " or need[0:5] == "o kno" or need[0:5] == "to kn":
                # Need to validate
                needs_Valid = True
                card_to_validate = group[0]
                value = validate_card(card_to_validate)
                print value

                r.sendline(value)

                need = r.recv()
                print need

                if need[0:3] == "card":
                    start = need[22:]
                    start = start[:-1]

                need = need[13 + 8:-2]
                setEnd = False

    if not needs_Valid:

        # Create random number. Length -2, as first 2 already added
        gen_code = ''.join(["%s" % randint(0, 9) for num in range(0, length - 2)])

        if setEnd:
            code = start + gen_code + end
            #print "code to test: " + code
        else:
            code = start + gen_code

        last_digit = code[-1]
        code_checker = code[:-1]
        without_last = code[:-1]

        code_checker = code_checker[::-1]  # Reverse

        # Multiple every other digit, starting at pos 0
        num_list = []
        for count, i in enumerate(code_checker):
            if count % 2 == 0:
                new_num = (int(i) * 2)
                if new_num > 9:
                    new_num = new_num - 9

                num_list.append(new_num)
            else:
                num_list.append(int(i))

        sum_list = sum(num_list)

        # code = without_last + str(sum_list % 10)
        code = without_last + str(int(((math.floor(sum_list / 10) + 1) * 10 - sum_list) % 10))
        # print "without: " + str(without_last)
        # print str(int(((math.floor(sum_list / 10) + 1) * 10.0 - sum_list) % 10))

        if setEnd:
            if str(code[len(code) - len(end):]) != end:
                #print end
                #print "str test: " + str(code[len(code) - len(end):]) + " = " + end
                continue

        #print code

        #print cardLuhnChecksumIsValid(code)
        #if cardLuhnChecksumIsValid(code):
        #    print "Success! " + code

        r.sendline(code)
        #print "here"

        need = r.recv()
        print need

        if need[0:3] == "card":
            start = need[22:]
            start = start[:-1]

        need = need[13 + 8:-2]
        setEnd = False
    needs_Valid = False
