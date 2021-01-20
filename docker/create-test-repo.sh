#!/bin/bash
export LC_ALL=C.UTF-8
export LANG=C.UTF-8

# install simpleaptrepo
pip3 install -e .

# do some cleanup
if [ -d "/repos/" ]; then
    rm -Rf /repos/
fi

# create a repo directory
mkdir /repos

# now we really create a repo here and add a package
# the gpg key is build into the docker image for testing purposes
simpleapt create-repo myrepo /repos --gpgkey B7C72A100F81017B
simpleapt add-component myrepo test
simpleapt list-repos
cp /usr/local/src/vdt/simpleaptrepo/tests/testdata/*.deb /repos/myrepo/test
simpleapt update-repo myrepo test
simpleapt update-repo myrepo test --skip-signed

# add the created repo as a local source
echo "deb file:/repos/myrepo/test /" > /etc/apt/sources.list.d/local.list

# add the GPG key as a valid key:
cat /repos/myrepo/test/keyfile | apt-key add -

# update the apt repository and install the signed package
apt-get update
apt-get install --yes testpackage