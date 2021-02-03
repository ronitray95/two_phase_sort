#include <string>
#include <fstream>

using namespace std;
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