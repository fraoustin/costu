# COSTU

inventaire d'une costumerie

## Usage by docker

    docker run -d -v <localpath>:/data --name costu -p 5000:80 fraoustin/costu

You can used the environment:

- COSTU_PORT default 5000
- COSTU_DEBUG default false
- COSTU_HOST default 0.0.0.0
- COSTU_DIR default /data

