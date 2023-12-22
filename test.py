import re
s = 'Â£45.17'
print(s)
z = re.findall(r'\d+\.\d+', s)[0]
print(z)
