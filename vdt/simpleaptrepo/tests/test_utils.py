import unittest

import vdt.simpleaptrepo.utils as utils


def mock_dist_osx():
    return "macOS-10.14.6-x86_64-i386-64bit"


def mock_dist_ubuntu():
    return "Linux-4.10.0-40-generic-x86_64-with-Ubuntu-16.04-xenial"


def mock_dist_debian():
    return "Linux-4.10.0-40-generic-x86_64-with-Debian-10"


class TestUtils(unittest.TestCase):
    def test_platform_is_debian(self):
        utils.platform.platform = mock_dist_osx
        self.assertFalse(utils.platform_is_debian())

        utils.platform.platform = mock_dist_ubuntu
        self.assertTrue(utils.platform_is_debian())

        utils.platform.platform = mock_dist_debian
        self.assertTrue(utils.platform_is_debian())
