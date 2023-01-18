import subprocess

subprocess.Popen(["git", "fetch"])
p = subprocess.Popen(["git", "status", "-uno"], stdout=subprocess.PIPE)

s = p.stdout.readlines()[1].decode()

print(len(s))