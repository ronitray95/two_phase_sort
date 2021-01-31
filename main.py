#!/usr/bin/env python3

import os
import sys
import tracemalloc
import itertools
from operator import itemgetter


columnSize = {}  # map of column names to size in bytes
columnList = []  # only column names with relative position
columnSort = []  # indices of columns to be sorted on
SINGLE_ROW_SIZE = 0
inpFile = ''
opFile = ''
memory = 0
sortOrder = ''


def check():
    global inpFile
    global opFile
    global memory
    global sortOrder
    global SINGLE_ROW_SIZE

    if not os.path.exists('metadata.txt'):
        print('Metadata not found')
        return False

    f = open('metadata.txt').readlines()
    for line in f:
        line = line.strip()
        line = line.split(',')
        try:
            columnSize[line[0]] = int(line[1])
            columnList.append(line[0])
            SINGLE_ROW_SIZE += int(line[1])
        except Exception:
            print('Non integer')
            return False

    l = len(sys.argv)
    if l < 6:
        print('Minimum cmd line args not provided')
        return False
    cmd = (sys.argv)
    inpFile = cmd[1]
    opFile = cmd[2]
    memory = int(cmd[3]) * 1000 * 1000 * 0.8
    sortOrder = (cmd[4]).lower()
    if sortOrder != 'asc' and sortOrder != 'desc':
        print('Unknown parameter', sortOrder)
        return False
    sortOrder = (True if sortOrder == 'desc' else False)
    for i in range(5, l):
        if cmd[i] not in columnSize:
            print('Unknown column', cmd[i])
            return False
        columnSort.append(columnList.index(cmd[i]))

    if not os.path.exists(inpFile):
        print(f'{inpFile} not found')
        return False

    return True


def main():
    if not check():
        return
    linesToRead = 100  # memory/SINGLE_ROW_SIZE
    charToRead = SINGLE_ROW_SIZE + 2 * (len(columnSize) - 1)
    f = open(inpFile)
    l = 0
    fcount = 1
    data = []
    print(f'Starting phase 1. Reading {linesToRead} at a time...')
    for line in f:
        # tracemalloc.start()
        # curr, peak = tracemalloc.get_traced_memory()
        # print(f"Current memory usage is {curr} B; Peak was {peak} B")
        new_list = []
        begIndex = 0
        for c in columnSize.keys():
            nst = line[begIndex:begIndex + columnSize[c]]
            new_list.append(nst)
            begIndex += columnSize[c]+2
        data.append(new_list)
        l += 1
        if l >= linesToRead:
            l = 0
            print('Sorting temporary block:', fcount)
            data = multisorted(data, columnSort)
            with open(f'temp{fcount}.txt', 'w') as newf:
                for d in data:
                    newf.write(' '.join(d))
                    newf.write('\n')
            data = []
            print(f'Writing to file temp{fcount}.txt')
            fcount += 1
    print('Total temporary files generated:', fcount)
    print('End of phase 1\n\n')


def multisorted(seq, indices):
    if len(indices) == 0:
        return seq
    #index = indices[0]
    partially_sorted_seq = sorted(
        seq, key=itemgetter(indices[0]), reverse=sortOrder)
    result = []
    for key, group in itertools.groupby(partially_sorted_seq, key=itemgetter(indices[0])):
        result.extend(multisorted(group, indices[1:]))
    return result


if __name__ == '__main__':
    main()
