import os 

files = os.listdir("data")

print(len(files))

f = []

for file in files:
    f.append( open("data/" +file, "r"))


with open("data/all_data.txt","w") as w:
    for _ in range(len(f[0].readlines())):
        for j in range(len(files)):
            w.write(f[j].readline())



