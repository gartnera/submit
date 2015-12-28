#include <unistd.h>

int main(int argc, char **argv)
{
	//must be absolute path
	char* interpreter = "/usr/bin/python";

	//should be absolute path (prevents environment attacks)
	char* source = "/usr/bin/submit.py";

	//one additional position for source name and one for NULL terminator
	char* args[argc + 3];

	//first argument will by overwriten by exec/python
	args[0] = interpreter;
	//second will be source file for the interpreter to execute
	args[1] = source;
	//third argment will be orginal program name
	args[2] = argv[0];

	//for each arg in argv, add to args
	int i, j;
	for (i = 3, j = 1; j < argc; ++i, ++j)
	{
		args[i] = argv[j];
	}
	//terminate args
	args[i] = NULL;

	//call command
	execv(interpreter, args);
	return 0;
}
