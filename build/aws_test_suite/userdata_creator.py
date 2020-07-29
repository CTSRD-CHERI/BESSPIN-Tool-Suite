import logging
import os


class UserdataCreator:
    """Create FETT Target userdata file to define workload on AWS instances"""

    def __init__(self, userdata=None):
        """
        Store userdata

        :param userdata: Userdata file to be sent to AWS instances
        :type userdata: str, list, optional

        :return: A new UserdataCreator instance
        :rtype: UserdataCreator
        """

        if userdata is None:
            userdata = []
        elif isinstance(userdata, str):
            userdata = userdata.split('\n')

        self._userdata = userdata

    @classmethod
    def with_fett_branch(cls, credentials, branch=None, binaries_branch=None, key_path='~/.ssh/id_rsa.pub'):
        """
        Add userdata to start with FETT Target at specific branch and binaries branch

        :param credentials: AWS credentials.
        :type credentials: AWSCredentials

        :param branch: What branch of SSITH-FETT-Target to run on AWS instances, defaults to 'master'
        :type branch: str, optional

        :param binaries_branch: What branch of SSITH-FETT-Binaries to run on AWS instances, defaults to 'master'
        :type binaries_branch: str, optional

        :param key_path: Path of the SSH public key, defaults to '~/.ssh/id_rsa.pub'
        :type key_path: str, optional

        :return: A new UserdataCreator instance
        :rtype: UserdataCreator
        """

        # Default branch on both
        if not (branch or binaries_branch):
            return cls()

        # If either branch is specified, we need to get a SSH key - best solution so far
        userdata = [
            "#!/bin/bash",
            "yum install -y git-lfs",
            "runuser -l centos -c 'sudo ssh-keyscan github.com >> ~/.ssh/known_hosts'",
            "cat >>/home/centos/.bashrc << EOL",
            f'export AWS_ACCESS_KEY_ID="{credentials.access_key_id}"',
            f'export AWS_SECRET_ACCESS_KEY="{credentials.secret_key_access}"',
            f'export AWS_SESSION_TOKEN="{credentials.session_token}"',
            "EOL",
        ]

        assert os.path.exists(os.path.expanduser(key_path)), f"key path {key_path} does not exist!"
        try:
            with open(os.path.expanduser(key_path), "r") as f:
                key = f.readlines()
                key = [x.strip() for x in key]
        except BaseException as e:
            logging.error("UserdataCreator: Invalid Key Path")
            logging.error(f"UserdataCreator: { e }")

        userdata_ssh = [
            "runuser -l centos -c 'touch /home/centos/.ssh/id_rsa'",
            "cat >/home/centos/.ssh/id_rsa <<EOL",
        ]
        userdata_ssh.extend(key + [
            "EOL",
            "runuser -l centos -c 'chmod 600 /home/centos/.ssh/id_rsa'",
            "ssh-keygen -y -f /home/centos/.ssh/id_rsa > ~/.ssh/id_rsa.pub"
        ])

        userdata += userdata_ssh

        # Compose userdata contents, depending on whether path was specified.
        # Binaries branch and Target branch provided
        userdata_specific = [
            f"""runuser -l centos -c 'ssh-agent bash -c "ssh-add /home/centos/.ssh/id_rsa && 
                cd /home/centos/SSITH-FETT-Target/ && 
                cd SSITH-FETT-Binaries && 
                git stash && 
                cd .. &&
                git fetch &&\n""" + (
                f"git checkout {branch} &&\n" if branch else "") +
            """git pull && 
                git submodule update && 
                cd SSITH-FETT-Binaries &&\n""" + (
                f"git checkout {binaries_branch} &&\n" if binaries_branch else "") +
            """git-lfs pull && 
                cd .. "'"""
        ]

        userdata += userdata_specific

        return cls(userdata)

    def append_to_userdata(self, ul=''):
        """
        Convenience to append to self._userdata

        :param ul: Script to append to userdata, defaults to ''
        :type ul: str, list, optional
        """

        if not isinstance(ul, str):
            self._userdata += ul
        else:
            self._userdata.append(ul)

    def append_file(self, dest, path):
        """
        Add file contents of path to userdata

        :param dest: Destination of file contents
        :type dest: str

        :param path: Filepath
        :type path: str
        """

        assert os.path.exists(path)
        self.append_to_userdata(f"cat > {dest} << EOL")
        with open(path, 'r') as f:
            self.append_to_userdata([line.strip() for line in f.readlines()])
        self.append_to_userdata("EOL")

    def to_file(self, fname):
        """
        Write userdata to a userdata file

        :param fname: Filename
        :type fname: str
        """
        with open(fname, 'w') as fp:
            ud = [f"runuser -l centos -c 'touch {self.indicator_filepath()}'"]
            fp.write('\n'.join(ud))
        logging.info(f"{self.__class__.__name__} wrote UserData to '{fname}'")

    @staticmethod
    def indicator_filepath():
        return "/home/centos/fett_userdata_complete"

    @property
    def userdata(self):
        """
        Userdata getter

        :return: Userdata
        :rtype: str
        """
        return '\n'.join(self._userdata)
