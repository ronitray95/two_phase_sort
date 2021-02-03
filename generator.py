#!/usr/bin/env python3

import random
import string
import sys


def makeFile():
    args = sys.argv  # num_lines file_name column sizes
    lines = int(args[1])
    fName = args[2]
    col_sizes = args[3:]

    with open(fName, 'w') as f:
        for i in range(0, lines):
            for j in col_sizes:
                x = ''.join(random.choices(string.digits + string.punctuation +
                                           string.ascii_uppercase + string.ascii_lowercase, k=int(j)))
                f.write(x)
                if col_sizes.index(j) != len(col_sizes)-1:
                    f.write('  ')
                # print(x)
            f.write('\n')

    with open('meta.txt', 'w') as f:
        for i in range(0, len(col_sizes)):
            f.write(f'c{i+1},{col_sizes[i]}')
            if i != len(col_sizes)-1:
                f.write('\n')

makeFile()
