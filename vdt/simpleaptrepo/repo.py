from glob import glob
import os
import subprocess

from vdt.simpleaptrepo.config import Config

from vdt.simpleaptrepo.utils import write_to_stdout


def create_gpg_key(output_command):
    cmd = "/usr/bin/gpg --gen-key"
    try:
        output_command(subprocess.check_output(cmd, shell=True))
    except subprocess.CalledProcessError as e:
        raise ValueError from e


def export_pubkey(path, gpgkey, output_command):
    key_path = os.path.join(path, "keyfile")
    cmd = "/usr/bin/gpg --digest-algo SHA256 --yes --output %s --armor --export %s" % (
        key_path,
        gpgkey,
    )
    subprocess.check_output(cmd, shell=True)
    output_command("Exported key %s to %s" % (gpgkey, key_path))


def sign_packages(path, gpgkey, skip_signed, output_command):
    # sign packages
    for deb_file in glob(os.path.join(path, "*.deb")):
        try:
            output = subprocess.check_output(
                "dpkg-sig --verify %s" % deb_file, shell=True
            )
        except subprocess.CalledProcessError as e:
            # this is pretty strange, as the command is returning an error code
            # but still could have run succesful
            output = e.output

        if b"_gpgbuilder" in output:

            if skip_signed:
                output_command("Skipped signing %s" % deb_file)
                continue

            output_command("Package %s already signed!" % deb_file)
            output_command("Removing signature")

            subprocess.check_output("ar -d %s _gpgbuilder" % deb_file, shell=True)

            # we should match the gpgbuilder output with a regex, but for now
            # we do this for a quickfix. The output can be _gpgbuilder or
            # _gpgbuilder0, probably _gpgbuilder1 etc too
            subprocess.check_output("ar -d %s _gpgbuilder0" % deb_file, shell=True)

        # sign again
        output_command("Signed package %s" % deb_file)
        subprocess.check_output(
            "/usr/bin/dpkg-sig -k %s --sign builder %s" % (gpgkey, deb_file), shell=True
        )


def create_package_index(path, output_command):
    output_command("Creates Packages")
    subprocess.check_output(
        "/usr/bin/apt-ftparchive packages . > Packages", shell=True, cwd=path
    )
    output_command("Creates Packages.gz")
    subprocess.check_output("/bin/gzip -c Packages > Packages.gz", shell=True, cwd=path)


def create_signed_releases_index(path, gpgkey, output_command):
    output_command("Create Release with key %s" % gpgkey)
    subprocess.check_output(
        "/usr/bin/apt-ftparchive release . > Release", shell=True, cwd=path
    )
    output_command("Create InRelease with key %s" % gpgkey)
    subprocess.check_output(
        "/usr/bin/gpg --digest-algo SHA256 --yes -u 0x%s --clearsign -o InRelease Release"
        % (gpgkey),
        shell=True,
        cwd=path,
    )
    output_command("Create Releases.gpg with key %s" % gpgkey)
    subprocess.check_output(
        "/usr/bin/gpg --yes -u 0x%s -abs -o Release.gpg Release" % (gpgkey),
        shell=True,
        cwd=path,
    )


class SimpleAPTRepo(Config):
    def add_repo(self, name, path, gpgkey=""):
        if not os.path.exists(path):
            raise ValueError("Path does not exists!")

        repo_dir = os.path.abspath(os.path.join(path, name))
        if os.path.exists(repo_dir):
            raise ValueError("Directory %s already exists!" % repo_dir)

        os.mkdir(repo_dir)

        self.add_repo_config(name, path=repo_dir, gpgkey=gpgkey)

    def add_component(self, name, component):
        repo_cfg = self.get_repo_config(name)

        path = os.path.join(repo_cfg["path"], component)
        if os.path.exists(path):
            raise ValueError("Directory %s already exists!" % path)
        os.mkdir(path)

        return path

    def get_component_path(self, name, component):
        repo_cfg = self.get_repo_config(name)
        path = os.path.join(repo_cfg.get("path"), component)
        if not os.path.exists(path):
            raise ValueError("Component '%s' does not exist!" % component)
        return path

    def list_repos(self):
        result = []
        for section in self.config.sections():
            repo = {}
            repo_cfg = self.get_repo_config(section)
            if repo_cfg.get("gpgkey"):
                section = "%s (gpgkey: %s)" % (section, repo_cfg.get("gpgkey"))
            repo["name"] = section
            repo["components"] = os.listdir(repo_cfg.get("path"))
            result.append(repo)
        return result

    def update_component(
        self, path, gpgkey=None, skip_signed=False, output_command=write_to_stdout
    ):
        if gpgkey is not None:
            # export keyfile
            export_pubkey(path, gpgkey, output_command)
            sign_packages(path, gpgkey, skip_signed, output_command)

        create_package_index(path, output_command)

        if gpgkey is not None:
            create_signed_releases_index(path, gpgkey, output_command)
