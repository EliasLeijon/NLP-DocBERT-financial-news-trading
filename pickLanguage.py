

file1 = open('processedData/processedNeutralNews.csv', 'r')
Lines = file1.readlines()

eng = open("english.txt", "a")
swe = open("swedish.txt", "a")

print("Look at news, if english: press 'a', if swedish press 'd' ")
# 352
for lindex, line in enumerate(Lines[351:]):
    print(line)
    key = input("eng (a) / swe (d)")
    print(key)
    if (key == "a"):
        eng.write(line)
    else:
        swe.write(line)
    print("line " + str(lindex) + " done")
