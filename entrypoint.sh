#!/bin/sh
set -e

if [ "$1" = 'costu' ]; then
    python -u /costu/costu.py
    exit
fi

exec "$@"