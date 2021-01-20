import configparser as ConfigParser

import os
import shutil
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

CREATE_REPO_NO_PARAMS_OUTPUT = """Usage: create-repo [OPTIONS] NAME [PATH]
Try 'create-repo --help' for help.

Error: Missing argument 'NAME'.
"""

LIST_REPOS_OUTPUT = """my_repo (gpgkey: 123456)
   main
"""

UPDATE_REPO_OUTPUT = """
Creates Packages
Creates Packages.gz
Create Release with key 123456
Create InRelease with key 123456
Create Releases.gpg with key 123456
"""


class TestCLI(unittest.TestCase):
    def setUp(self):
        # patch the aptrepo instance to write the file to the current
        # directory, re-read the sections
        cli.apt_repo.path = os.path.join(os.getcwd(), ".simpleapt.ini")
        cli.apt_repo.config.read(cli.apt_repo.path)
        cli.apt_repo.sections = cli.apt_repo.config.sections()

    def tearDown(self):
        # remove the config file when it exists, and clear the sections
        if os.path.exists(cli.apt_repo.path):
            os.remove(cli.apt_repo.path)

        # remove repo artifacts
        my_repo = os.path.join(os.getcwd(), "my_repo")

        if os.path.exists(my_repo):
            shutil.rmtree(my_repo)

        cli.apt_repo.config = ConfigParser.ConfigParser()

    @mock.patch("subprocess.check_output", return_value="GPG OUTPUT")
    def test_create_gpg_key(self, mock_subprocess):
        runner = CliRunner()
        result = runner.invoke(cli.create_key)

        # command should be run without error
        self.assertEqual(result.exit_code, 0)
        # and our mock functions should have been called
        self.assertTrue(mock_subprocess.called)
        # click's output should be captured correctly
        self.assertEqual(result.output, GPG_KEY_OUTPUT)

    @mock.patch("subprocess.check_output", side_effect=ValueError("GPG ERROR"))
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
            result = runner.invoke(cli.create_repo, ["my_repo", "--gpgkey", "123456"])

            # command should be run without error
            self.assertEqual(result.exit_code, 0)

            # click's output should be captured correctly
            self.assertEqual(result.output, CREATE_REPO_OUTPUT)

            # a directory with 'my_repo' should be here
            self.assertTrue(os.path.exists("my_repo"))

            # a configuration file in my home directory should be there
            self.assertTrue(os.path.exists(cli.apt_repo.path))

            # now create a component
            result = runner.invoke(cli.add_component, ["my_repo", "main"])

            # command should be run without error
            self.assertEqual(result.exit_code, 0)

            # click's output should be captured correctly
            self.assertTrue(
                "Add http://<hostname>/my_repo/main / to your sources.list"
                in result.output
            )  # noqa

            # adding the same component should raise an error
            result = runner.invoke(cli.add_component, ["my_repo", "main"])

            self.assertEqual(result.exit_code, 2)
            self.assertTrue("already exists!" in result.output)

            # now we create another repo without a gpg key
            result = runner.invoke(cli.create_repo, ["another_repo"])

            # a directory with 'my_repo' should be here
            self.assertTrue(os.path.exists("another_repo"))

            # now create a component
            result = runner.invoke(cli.add_component, ["another_repo", "main"])

            # command should be run without error
            self.assertEqual(result.exit_code, 0)

            # click's output should be captured correctly
            self.assertTrue(
                "Add http://<hostname>/another_repo/main / to your sources.list"
                in result.output
            )  # noqa

    def test_create_repo_unkown_path(self):
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(cli.create_repo, ["my_repo", "/unknown/path/"])

            # there is an error as the path is unknown
            self.assertEqual(result.exit_code, 2)
            self.assertIn("Path does not exists!", result.output)

    def test_create_repo_no_params(self):
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(cli.create_repo)

            # there is an error as we did not pass any parameter
            self.assertEqual(result.exit_code, 2)
            self.assertIn(CREATE_REPO_NO_PARAMS_OUTPUT, result.output)

    def test_list_repos(self):
        runner = CliRunner()
        runner.echo_stdin = True

        # create a repo and a component
        with runner.isolated_filesystem():
            result = runner.invoke(cli.create_repo, ["my_repo", "--gpgkey", "123456"])
            self.assertEqual(result.exit_code, 0)
            result = runner.invoke(cli.add_component, ["my_repo", "main"])
            self.assertEqual(result.exit_code, 0)

            # make sure list_repos is showing the correct output
            result = runner.invoke(cli.list_repos)
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(result.output, LIST_REPOS_OUTPUT)

    @mock.patch("subprocess.check_output", return_value="Mocked output")
    def test_update_repo(self, mock_subprocess=None):  # pylint: disable=W0613
        runner = CliRunner()

        with runner.isolated_filesystem():
            # create a repo and a component
            result = runner.invoke(cli.create_repo, ["my_repo", "--gpgkey", "123456"])
            self.assertEqual(result.exit_code, 0)
            result = runner.invoke(cli.add_component, ["my_repo", "main"])
            self.assertEqual(result.exit_code, 0)

            # we mock everything, however, the runner still should say that
            # everything is created / updated
            result = runner.invoke(cli.update_repo, ["my_repo", "main"])
            self.assertEqual(result.exit_code, 0)
            self.assertIn(UPDATE_REPO_OUTPUT, result.output)

            # Let's update an component which does not exist
            result = runner.invoke(cli.update_repo, ["my_repo", "i-am-not-there"])
            self.assertEqual(result.exit_code, 2)
            self.assertIn("Component 'i-am-not-there' does not exist!", result.output)
