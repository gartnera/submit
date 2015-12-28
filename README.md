# Submit

Submit is a tool which allows teachers to create assignments and deadlines for users on a shared (Linux) development environment. Students can then view which assignments they can submit and submit code to those assignments. Think of it like a CLI dropbox.

# Program General Overview
submit provides two main components, the administrator/teacher side, and a student side. When invoked as `submit -m` by a teacher, the teacher can add/edit/delete assignments, as well as view submitted assignments and grade them. When invoked as `submit -l`, the program lists all the assignments a student can submit. When invoked as `submit <filename>`, the user will be prompted which class and assignment they want to submit the file to.

# Program Technical Overview
When a student runs submit, we look to see which groups the student is a member of. Based on those groups, a student can view and submit assignments to the classes associated with those groups. For each class there is also an administrator/teacher based on the user id of that user.

Submit is really dependent on the set user id (SUID) of Linux environment. We create a user called `submit` which contains all the data submitted by students and entered by teacher. When a user invokes submit, the process is running with the priviledges of a process invoked by the submit user theirself. By doing this, we can keep the submit information private, while establishing a communication path between the user and the submit system. The submit binary itself is just a wrapper around a python script which contains the core logic of this project, since (python) scripts can't be SUID.

When submit is executed, we load `classes.json` which is created/modified by `bin/provision-classes.py`. Administrators(s) who can log directly into submit can use this script to establish or delete class sections. Based on `classes.json`, we prompt the user for which class they want to work with. Each class has a directory in the `content\` folder which contains another file called `assignments.json` which contains further information about the assignments for the selected class.

# Installation
Note: I've only tested installation on Debian 8. You'll need to change the `bin/deploy-root.sh` file if you want to use a different distribution

Run the following steps as root:

1. Create a user called submit
	* `useradd submit -s /bin/bash`
2. Copy the project files into /home/
	* `cd /home/`
	* `wget https://github.com/gartnera/submit/archive/master.tar.gz -O - | tar xz`
	* `mv submit-master submit`
3. Set the ownership of submit/ to submit
	* `chown -R submit:submit /home/submit`
4. As root, we need to install dependencies and setup binaries
	* `cd /home/submit/`
  * `./bin/deploy-root.sh`
5. After that we need to su to submit and deploy a few more things. When we su to submit `/home/submit/bin/` will be in our path
  * `su - submit`
  * `deploy-submit.sh`
6. At this stage, everything is installed. Now you can execute `provision-classes.py` to create/edit/delete classes.
  * `provision-classes.py`
