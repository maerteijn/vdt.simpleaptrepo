import click
from vdt.simpleaptrepo.repo import create_gpg_key, SimpleAPTRepo
from vdt.simpleaptrepo.utils import platform_is_debian, repo_root

apt_repo = SimpleAPTRepo()


@click.group()
def cli():
    pass


@cli.command(name="create-gpg-key")
def create_key():
    """Creates a GPG key"""
    try:
        create_gpg_key(output_command=click.echo)
    except ValueError as e:
        raise click.UsageError(str(e))

    click.echo("Key created (see above for the hash)")
    click.echo("Now add a repository with the 'create-repo' command")


@cli.command(name="create-repo")
@click.argument("name")
@click.argument("path", default=".")
@click.option("--gpgkey", help="The GPG key to sign the packages with")
def create_repo(name, path, gpgkey=""):
    """Creates a repository"""
    try:
        apt_repo.add_repo(name, path, gpgkey)
    except ValueError as e:
        raise click.BadParameter(str(e))

    click.echo("Repository '%s' created" % name)
    click.echo("Now add a component with the 'add-component' command")


@cli.command(name="add-component")
@click.argument("name")
@click.argument("component", default="main")
def add_component(name, component):
    """Creates a component (ie, 'main', 'production')"""
    try:
        path = apt_repo.add_component(name, component)
    except ValueError as e:
        raise click.BadParameter(str(e))

    root = repo_root(path)

    click.echo("Component '%s' created in repo '%s'" % (component, name))
    click.echo("Now add some unsigned debian packages in the directory")
    click.echo("and run the 'update-repo' command")
    click.echo("")
    click.echo(
        "After that, configure your webservice " "to set the www-root to %s " % root
    )
    click.echo("Add http://<hostname>/%s/%s / to your sources.list" % (name, component))
    click.echo("")
    click.echo("Add the key on the host where you want to install the packages.")
    click.echo("(This is only needed once per repository)")
    click.echo(
        "wget -qO - http://<hostname>/%s/%s/keyfile | sudo apt-key add -"
        % (name, component)
    )


@cli.command(name="update-repo")
@click.argument("name")
@click.argument("component", default="main")
@click.option("--skip-signed", is_flag=True, help="Skip already signed packaged")
def update_repo(name, component, skip_signed=False):
    """Updates a repo's component by scanning the debian packages
    and add the index files.
    """
    try:
        repo_cfg = apt_repo.get_repo_config(name)
        component_path = apt_repo.get_component_path(name, component)
    except ValueError as e:
        raise click.BadParameter(str(e))

    gpgkey = repo_cfg.get("gpgkey", None)

    apt_repo.update_component(
        component_path, gpgkey, skip_signed, output_command=click.echo
    )


@cli.command("list-repos")
def list_repos():
    """List currently configured repos"""
    repos = apt_repo.list_repos()
    for repo in repos:
        click.echo(repo.get("name"))
        for component in repo.get("components"):
            click.echo("   {0}".format(component))


def main():
    if platform_is_debian():
        cli()
    else:
        click.echo("You are not on debian or ubuntu, aborting!")


if __name__ == "__main__":
    main()
