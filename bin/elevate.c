#include <unistd.h>

int main(int argc, char **argv)
{
	int uid = geteuid();

	setreuid(uid, uid);

	//one additional position for NULL terminator
	char* args[argc + 1];

	//for each arg in argv, add to args
	int i;
	for (i = 0; i < argc; ++i)
	{
		args[i] = argv[i];
	}
	//terminate args
	args[i] = NULL;

	//call command
	//specify CMD with gcc -DCMD='"/my/absolute/path"'
	//need double quotes (one for bash, one to pass in)
	execv(CMD, args);
	return 0;
}
