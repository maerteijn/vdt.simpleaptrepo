import os
import platform
import sys


def repo_root(path):
    """
    Returns the root directory from a repo/component

    >>> repo_root("/www/myrepo/test")
    '/www'

    >>> repo_root("/home/user/myrepo/staging")
    '/home/user'

    >>> repo_root("/myrepo/staging")
    '/'

    """
    return os.path.split(os.path.split(path)[0])[0]


def write_to_stdout(message):
    unbuffered_output = os.fdopen(sys.stdout.fileno(), "w", 0)
    unbuffered_output.write("%s\n" % message)


def platform_is_debian():
    current_platform = platform.platform().lower()
    return "ubuntu" in current_platform or "debian" in current_platform
