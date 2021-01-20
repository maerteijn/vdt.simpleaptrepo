import os
import unittest

import vdt.simpleaptrepo.config as config


class TestConfig(unittest.TestCase):
    def setUp(self):
        config.HOME = os.getcwd()
        self.configfile = os.path.join(os.getcwd(), ".simpleapt.ini")

    def tearDown(self):
        # remove the config file
        os.remove(self.configfile)

    def test_create_config_file(self):
        # this should create a configfile
        config_obj = config.Config()
        config_obj.save_config()
        os.path.isfile(self.configfile)

    def test_add_repo_config(self):
        # adds a repo to the configfile
        config_obj = config.Config()
        config_obj.add_repo_config(name="test", path="/www", gpgkey="123456")

        # check the values of path and gpgkey
        section = config_obj.config.items("test")
        self.assertEqual(section[0][1], "/www")
        self.assertEqual(section[1][1], "123456")

    def test_get_repo_config(self):
        config_obj = config.Config()
        config_obj.add_repo_config(name="test", path="/www", gpgkey="123456")

        # this should be fine
        cfg = config_obj.get_repo_config(name="test")
        self.assertTrue("path" in cfg)
        self.assertTrue("gpgkey" in cfg)

        # a unkown name should raise an exception
        self.assertRaises(ValueError, config_obj.get_repo_config, "unkown")
