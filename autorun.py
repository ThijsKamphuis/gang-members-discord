import subprocess

p = subprocess.Popen(["git", "status", "-uno"], stdout=subprocess.PIPE)

s = p.stdout.readline().decode()
#
print(s)