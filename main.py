#!/usr/bin/env python3

import os
import sys
import tempfile
import tracemalloc
import itertools
from operator import itemgetter

from heap import HeapNode

columnSize = {}  # map of column names to size in bytes
columnList = []  # only column names with relative position
columnSort = []  # indices of columns to be sorted on
SINGLE_ROW_SIZE = 0
inpFile = ''
opFile = ''
memory = 0
sortOrder = ''
tempFilePointers = []
MAX_STRING = f'{chr(254)}'
MIN_STRING = ''


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
            tf = tempfile.NamedTemporaryFile(
                mode='w+t', prefix='temp_', suffix=f'_{fcount}.txt', dir=os.getcwd(), delete=False)
            # with open(f'temp{fcount}.txt', 'w') as newf:
            for d in data:
                tf.writelines(' '.join(d))
                tf.writelines('\n')
            tf.seek(0)
            tempFilePointers.append(tf)
            data = []
            print(f'Writing to file {tf.name}.txt')
            fcount += 1
    print('Total temporary files generated:', fcount)
    f.close()
    print('End of phase 1\n\n')

    print('Starting phase 2. Merging files...')
    buffer = []
    op = open(opFile, 'w')

    for tf in tempFilePointers:
        # list of first string from all temp files with their pointers
        buffer.append(HeapNode(tf.readline(), tf))

    buildHeap(buffer)
    while True:
        node = buffer[0]
        if node.data == MAX_STRING or node.data == MIN_STRING:
            break
        op.writelines(node.data)
        new_line = node.filepointer.readline()
        if not new_line:
            new_line = MIN_STRING if sortOrder else MAX_STRING
        buffer[0] = HeapNode(new_line, node.filepointer)
        heapify(buffer, 0, len(buffer))
    op.close()

    print('Finished merging. Deleting temporary files')
    for tf in tempFilePointers:
        s = tf.name
        os.remove(tf.name)
        print(f'Deleted file {s}')


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


def aGreaterThanB(lstA, lstB):
    new_list = []
    begIndex = 0
    for c in columnSize.keys():
        nst = lstA[begIndex:begIndex + columnSize[c]]
        new_list.append(nst)
        begIndex += columnSize[c]+1
    lstA = new_list

    new_list = []
    begIndex = 0
    for c in columnSize.keys():
        nst = lstB[begIndex:begIndex + columnSize[c]]
        new_list.append(nst)
        begIndex += columnSize[c]+1
    lstB = new_list
    new_list = []

    for i in columnSort:
        if lstA[i] == lstB[i]:
            continue
        if lstA[i] > lstB[i]:
            return True
        else:
            return False
    return True


def aLesserThanB(lstA, lstB):
    new_list = []
    begIndex = 0
    for c in columnSize.keys():
        nst = lstA[begIndex:begIndex + columnSize[c]]
        new_list.append(nst)
        begIndex += columnSize[c]+1
    lstA = new_list

    new_list = []
    begIndex = 0
    for c in columnSize.keys():
        nst = lstB[begIndex:begIndex + columnSize[c]]
        new_list.append(nst)
        begIndex += columnSize[c]+1
    lstB = new_list
    new_list = []

    for i in columnSort:
        if lstA[i] == lstB[i]:
            continue
        if lstA[i] < lstB[i]:
            return True
        else:
            return False
    return True


def heapify(block, i, n):
    left = 2 * i + 1
    right = 2 * i + 2  # sortType=false for asc and true for desc
    sortResult = left < n and (aGreaterThanB(block[left].data, block[i].data) if sortOrder else aLesserThanB(
        block[left].data, block[i].data))

    if left < n and sortResult:
        smallest = left
    else:
        smallest = i

    sortResult = right < n and (aGreaterThanB(block[right].data, block[smallest].data) if sortOrder else aLesserThanB(
        block[right].data, block[smallest].data))

    if right < n and sortResult:
        smallest = right

    if i != smallest:
        (block[i], block[smallest]) = (block[smallest], block[i])
        heapify(block, smallest, n)


def buildHeap(arr):
    l = len(arr)  # - 1
    mid = int(l / 2)-1
    while mid >= 0:
        heapify(arr, mid, l)
        mid -= 1


if __name__ == '__main__':
    main()
