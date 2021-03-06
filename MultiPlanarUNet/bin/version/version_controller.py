import subprocess
import os


class VersionController(object):
    def __init__(self, logger=None):
        import MultiPlanarUNet
        from MultiPlanarUNet.logging import ScreenLogger
        code_path = MultiPlanarUNet.__path__
        assert len(code_path) == 1
        self.logger = logger or ScreenLogger()
        self.git_path = os.path.abspath(code_path[0])
        self._mem_path = None

    def log_version(self, logger=None):
        logger = logger or self.logger
        logger("MultiPlanarUNet version: {} ({}, {})".format(self.version,
                                                             self.branch,
                                                             self.current_commit))

    def __enter__(self):
        self._mem_path = os.getcwd()
        os.chdir(self.git_path)

    def __exit__(self, exc_type, exc_val, exc_tb):
        os.chdir(self._mem_path)
        self._mem_path = None

    def git_query(self, string):
        with self:
            p = subprocess.Popen(string.split(), stdout=subprocess.PIPE)
            out, _ = p.communicate()
            out = out.decode("utf-8").strip(" \n")
        return out

    @property
    def remote_url(self):
        return self.git_query("git config --get remote.origin.url")

    @property
    def version(self):
        from MultiPlanarUNet import __version__
        return __version__

    @property
    def current_commit(self):
        return self.git_query("git rev-parse --short HEAD")

    def get_latest_commit_in_branch(self, branch=None):
        branch = branch or self.branch
        url = self.remote_url
        return self.git_query("git ls-remote {} refs/heads/{}".format(
            url, branch
        ))[:7]

    @property
    def branch(self):
        return self.git_query("git symbolic-ref --short HEAD")

    def set_commit(self, commit_id):
        self.git_query("git reset --hard {}".format(str(commit_id)[:7]))

    def set_branch(self, branch):
        self.git_query("git checkout {}".format(branch))

    def set_version(self, version):
        version = str(version).lower().strip(" v")
        self.set_branch("v{}".format(version))
        self.set_commit(self.get_latest_commit_in_branch())
