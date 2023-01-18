import subprocess

subprocess.Popen(["git", "fetch"])
p = subprocess.Popen(["git", "status", "-uno"], stdout=subprocess.PIPE)

s = [l.decode() for l in p.stdout.readlines()]

print(s)