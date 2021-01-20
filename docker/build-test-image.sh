#!/bin/bash

# build the image
docker build -t maerteijn/simpeapt-test-image .

# run a interactive shell and you should generate a gpg key
echo "Please run /usr/bin/gpg --digest-algo SHA256 --gen-key, then exit the container with ctrl+D"
docker run -it --name=simpleapt-test-image-generate-key maerteijn/simpeapt-test-image /bin/bash

echo "Please remember the generated GPG key hash"
echo "Committing changes to the docker image"
docker commit simpleapt-test-image-generate-key maerteijn/simpeapt-test-image

echo "Done!"
echo "Now push the image with 'docker push maerteijn/simpeapt-test-image'"
echo "and delete the container afterwards: 'docker rm simpleapt-test-image-generate-key'"
