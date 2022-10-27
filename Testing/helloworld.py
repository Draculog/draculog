import sys

size = 0
algo = 'b'
if len(sys.argv) > 1:
    size = int(sys.argv[1])
    print(str(sys.argv[1]), end="")
    if len(sys.argv) > 2:
        algo = sys.argv[2]
        print(" " + str(sys.argv[2]), end="")

print("\tHello World!")

if size > 150000 and algo == 's':
    prin("Hate Errors")
    sys.exit(1)


