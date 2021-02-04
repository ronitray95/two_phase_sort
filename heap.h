#include <string>
#include <fstream>

class HeapNode
{
public:
	std::string data;
	FILE* filePointer;
	HeapNode()
	{
		data = "";
		filePointer = NULL;
	}
	HeapNode(std::string d, FILE* f)
	{
		data = d;
		filePointer = f;
	}
};