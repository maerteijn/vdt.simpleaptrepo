import configparser as ConfigParser

import os

HOME = os.path.expanduser("~")


class Config(object):
    def __init__(self):
        self.config = ConfigParser.ConfigParser()
        self.path = os.path.join(HOME, ".simpleapt.ini")
        self.config.read(self.path)

    def save_config(self):
        self.config.write(open(self.path, "w"))
        self.config.read(self.path)

    def add_repo_config(self, name, path, gpgkey=""):
        if not self.config.has_section(name):
            self.config.add_section(name)

        self.config.set(name, 'path', path)

        if gpgkey:
            self.config.set(name, 'gpgkey', gpgkey)

        self.save_config()

    def get_repo_config(self, name):
        if not self.config.has_section(name):
            raise ValueError("'%s' does not exist!" % name)
        return dict(self.config.items(name))
