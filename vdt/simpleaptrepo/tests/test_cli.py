import os
import unittest


from click.testing import CliRunner

import mock

from vdt.simpleaptrepo import cli


GPG_KEY_OUTPUT = """GPG OUTPUT
Key created (see above for the hash)
Now add a repository with the 'create-repo' command
"""

GPG_KEY_ERROR = """Usage: create-gpg-key [OPTIONS]

Error: GPG ERROR
"""

CREATE_REPO_OUTPUT = """Repository 'my_repo' created
Now add a component with the 'add-component' command
"""


class TestCLI(unittest.TestCase):

    def setUp(self):
        # patch the aptrepo instance to write the file to the current
        # directory, re-read the sections
        cli.apt_repo.path = os.path.join(os.getcwd(), ".simpleapt.ini")
        cli.apt_repo.config.read(cli.apt_repo.path)
        cli.apt_repo.sections = cli.apt_repo.config.sections()

    @mock.patch('subprocess.check_output', return_value="GPG OUTPUT")
    def test_create_gpg_key(self, mock_subprocess):
        runner = CliRunner()
        result = runner.invoke(cli.create_key)

        # command should be run without error
        self.assertEqual(result.exit_code, 0)
        # and our mock functions should have been called
        self.assertTrue(mock_subprocess.called)
        # click's output should be captured correctly
        self.assertEqual(result.output, GPG_KEY_OUTPUT)

    @mock.patch('subprocess.check_output', side_effect=ValueError('GPG ERROR'))
    def test_create_gpg_key_exception(self, mock_subprocess):
        runner = CliRunner()
        result = runner.invoke(cli.create_key)

        # command should raise an error
        self.assertEqual(result.exit_code, 2)
        # and our mock functions should have been called
        self.assertTrue(mock_subprocess.called)
        # click's output should be captured correctly
        self.assertEqual(result.output, GPG_KEY_ERROR)

    def test_create_repo_and_component(self):
        runner = CliRunner()

        with runner.isolated_filesystem():
            result = runner.invoke(
                cli.create_repo, ["my_repo", "--gpgkey", "123456"])

            # command should be run without error
            self.assertEqual(result.exit_code, 0)

            # click's output should be captured correctly
            self.assertEqual(result.output, CREATE_REPO_OUTPUT)

            # a directory with 'my_repo' should be here
            self.assertTrue(os.path.exists("my_repo"))

            # a configuration file in my home directory should be there
            self.assertTrue(os.path.exists(cli.apt_repo.path))

            # now create a component
            result = runner.invoke(
                cli.add_component, ["my_repo", "main"])

            # command should be run without error
            self.assertEqual(result.exit_code, 0)

            # click's output should be captured correctly
            self.assertTrue(
                "Add http://<hostname>/my_repo/main / to your sources.list" in result.output)  # noqa

    def tearDown(self):
        # remove the config file when it exists
        if os.path.exists(cli.apt_repo.path):
            os.remove(cli.apt_repo.path)