import subprocess

subprocess.Popen(["git", "fetch"])
p = subprocess.Popen(["git", "status", "-uno"], stdout=subprocess.PIPE)

s = p.stdout.readlines()[1].decode()

if len(s) > 50:
    subprocess.Popen(["git", "pull"])
    subprocess.Popen(["systemctl", "restart", "gang-members-discord"])#