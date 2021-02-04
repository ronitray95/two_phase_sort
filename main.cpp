#include <fstream>
#include <vector>
#include <string>
#include <iostream>
#include <algorithm>

#include <stdio.h>

#include "heap.h"

using namespace std;

vector<string> columnNames; // column names
vector<int> columnSizes;    // only column names with relative position
vector<int> columnSort;     // indices of columns to be sorted on
vector<int> columnPositions;
int SINGLE_ROW_SIZE = 0;
long long linesInFile = 0;
string inpFile = "";
string opFile = "";
long long memory = 0;
bool sortOrder = false; //false=asc,true=desc
vector<FILE *> filePointers;
string MAX_STRING = "";
string MIN_STRING = "";

bool compareString(string s1, string s2)
{
    for (int i = 0; i < columnSort.size(); i++)
    {
        int pos = columnSort[i];
        string a = s1.length() <= 1 ? s1 : s1.substr(columnPositions[pos], columnSizes[pos]);
        string b = s2.length() <= 1 ? s2 : s2.substr(columnPositions[pos], columnSizes[pos]);
        if (a == b)
            continue;
        if (sortOrder)
            return b < a;
        else if (!sortOrder)
            return a < b;
    }
    return false;
}

void heapify(HeapNode *block, int i, int n)
{
    int left = 2 * i + 1;
    int right = 2 * i + 2; // sortType=false for asc and true for desc
    bool sortResult = left < n && compareString(block[left].data, block[i].data);
    int smallest;
    if (left < n && sortResult)
        smallest = left;
    else
        smallest = i;

    sortResult = right < n && compareString(block[right].data, block[smallest].data);
    if (right < n && sortResult)
        smallest = right;
    if (i != smallest)
    {
        swap(block[i], block[smallest]);
        heapify(block, smallest, n);
    }
}

void buildHeap(HeapNode *arr, int l)
{
    int mid = l / 2 - 1;
    while (mid >= 0)
    {
        heapify(arr, mid, l);
        mid -= 1;
    }
}

bool check(int argc, char **argv)
{
    MAX_STRING += ((char)254);
    ifstream meta("metadata.txt");
    if (!meta)
    {
        cout << "Metadata not found\n";
        return false;
    }
    string x;
    getline(meta, x);
    int pos = 0;
    while (meta)
    {
        int i = x.find(",");
        columnPositions.push_back(pos);
        columnNames.push_back(x.substr(0, i));
        int r = stoi(x.substr(i + 1));
        SINGLE_ROW_SIZE += r;
        columnSizes.push_back(r);
        pos += (r + 2);
        getline(meta, x);
    }
    meta.close();
    if (argc < 6)
    {
        cout << "Minimum cmd line args not provided\n";
        return false;
    }
    inpFile = string(argv[1]);
    opFile = string(argv[2]);
    memory = stoi(argv[3]) * 1000 * 1000 * 0.6;
    string ss = string(argv[4]);
    transform(ss.begin(), ss.end(), ss.begin(), ::tolower);
    if (ss != "asc" and ss != "desc")
    {
        cout << "Unknown parameter " << ss << endl;
        return false;
    }
    sortOrder = ss != "asc";
    for (int i = 5; i < argc; i++)
    {
        string c = argv[i];
        auto a = find(columnNames.begin(), columnNames.end(), c);
        if (a == columnNames.end())
        {
            cout << "Illegal column " << c << endl;
            return false;
        }
        columnSort.push_back(a - columnNames.begin());
    }
    ifstream ip(inpFile);
    if (!ip)
    {
        cout << "Input file not found: " << inpFile << endl;
        return false;
    }
    ip.close();
    return true;
}

int main(int argc, char **argv)
{
    if (!check(argc, argv))
        return -1;
    FILE *fp;
    fp = fopen(inpFile.c_str(), "r");
    while (EOF != (fscanf(fp, "%*[^\n]"), fscanf(fp, "%*c")))
        ++linesInFile;
    printf("Total Lines in file : %lld\n", linesInFile);
    if (memory * memory < linesInFile * SINGLE_ROW_SIZE)
    {
        printf("File is too big for 2 way merge sort. K way merge sort is needed.");
        return -1;
    }
    long long linestoRead = memory / SINGLE_ROW_SIZE;
    linestoRead = min(linesInFile, linestoRead);
    ifstream ip(inpFile);
    string line;
    getline(ip, line);
    int l = 0, fcount = 0;
    vector<string> data;
    data.reserve(linestoRead);
    printf("Starting phase 1. Reading %lld at a time...\n", linestoRead);
    while (ip)
    {
        l++;
        if (line.length() >= SINGLE_ROW_SIZE)
        {
            line.erase(remove(line.begin(), line.end(), '\n'), line.end());
            line.erase(remove(line.begin(), line.end(), '\r'), line.end());
            data.push_back(line);
        }
        getline(ip, line);
        if (l >= linestoRead)
        {
            l = 0;
            fcount++;
            printf("Sorting temporary block: %d\n", fcount);
            sort(data.begin(), data.end(), compareString);
            printf("Sorted!\n");
            string fName = "temp_" + to_string(fcount) + ".txt";
            ofstream out(fName);
            printf("Writing to file %s\n", fName.c_str());
            for (string s : data)
                out << s << "\n";
            out.close();
            FILE *f = fopen(fName.c_str(), "r");
            filePointers.push_back(f);
            printf("Write done!\n");
            data.clear();
        }
    }
    ip.close();
    printf("Full input file read\n");
    if (data.size() != 0)
    {
        fcount++;
        printf("Sorting temporary block: %d\n", fcount);
        sort(data.begin(), data.end(), compareString);
        printf("Sorted!\n");
        string fName = "temp_" + to_string(fcount) + ".txt";
        ofstream out(fName);
        printf("Writing to file %s\n", fName.c_str());
        for (string s : data)
            out << s << "\n";
        out.close();
        FILE *f = fopen(fName.c_str(), "r");
        filePointers.push_back(f);
        printf("Write done!\n");
    }
    vector<string>().swap(data); //deallocate
    printf("Total temporary files generated: %d\n", fcount);
    printf("End of phase 1\nStarting phase 2. Merging files...\n");
    HeapNode buffer[fcount];
    ofstream op(opFile);
    for (int i = 0; i < fcount; i++)
    {
        FILE *f = filePointers[i];
        char x[SINGLE_ROW_SIZE + 10];
        fgets(x, SINGLE_ROW_SIZE + 10, f);
        strtok(x, "\n");
        buffer[i] = HeapNode(string(x), f);
    }
    buildHeap(buffer, fcount);
    cout << "Heap built\n";
    while (true)
    {
        HeapNode node = buffer[0];
        if (node.data == MAX_STRING || node.data == MIN_STRING)
            break;
        op << node.data << "\n";
        char x[SINGLE_ROW_SIZE + 10];
        char *isNull = fgets(x, SINGLE_ROW_SIZE + 10, node.filePointer);
        strtok(x, "\n");
        string new_line = "";
        if (!isNull)
            new_line = (sortOrder ? MIN_STRING : MAX_STRING);
        else
            new_line = string(x);
        buffer[0] = HeapNode(new_line, node.filePointer);
        heapify(buffer, 0, fcount);
    }
    op.close();
    printf("Finished merging. Deleting temporary files\n");
    for (int i = 0; i < fcount; i++)
    {
        fclose(filePointers[i]);
        int x = remove(("temp_" + to_string(i + 1) + ".txt").c_str());
        if (x == 0)
            printf("Deleted temp file temp_%d.txt\n", i + 1);
        else
            printf("Failed to delete temp file temp_%d.txt\n", i + 1);
    }
}