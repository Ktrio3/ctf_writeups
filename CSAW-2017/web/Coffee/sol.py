# This is only the first part of the solution; the other half I didn't get

def java_string_hashcode(s):
    h = 0
    for c in s:
        h = (31 * h + ord(c)) & 0xFFFFFFFF
    return ((h + 0x80000000) & 0xFFFFFFFF) - 0x80000000


string_to_collide = raw_input("Enter string to collide: ")

original_value = java_string_hashcode(string_to_collide)

print "original_value: " + str(original_value)

new_string = ""

for char in string_to_collide:
    if char.isalnum():
        new_string = new_string + char
    else:
        final_string = new_string[:-1]
        # We cannot use the last value, in case our value is below 0, such as $
        new_string = new_string[:-1] + "0" * (len(string_to_collide) - len(new_string) + 1)
        break
print "Closest: " + new_string

current_value = java_string_hashcode(new_string)

current_place = len(final_string)

while current_value != original_value:
    current_char = new_string[current_place]
    last_char = current_char
    # print current_value, original_value

    while current_value <= original_value:
        last_char = current_char

        if current_char == "9":
            current_char = "A"
        elif current_char == "Z":
            current_char = "a"
        elif current_char == "z":
            exit("Failure")
        else:
            current_char = chr(ord(current_char) + 1)

        string_to_test = new_string[0:current_place] + current_char + new_string[current_place + 1:]
        current_value = java_string_hashcode(string_to_test)

    new_string = new_string[0:current_place] + last_char + new_string[current_place + 1:]
    current_place = current_place + 1
    current_value = java_string_hashcode(new_string)
    print new_string
    print str(current_value) + " " + str(original_value)

print new_string
