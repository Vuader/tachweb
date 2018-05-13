#!/usr/bin/env /bin/bash

function run {
    "$@"
    local status=$?
    if [ $status -ne 0 ]; then
        echo "error with $1" >&2
        exit $status
    fi
}

if [ -f $virtualenv/bin/activate ]; then
    run source $virtualenv/bin/activate
    run pip3 install --upgrade pip
    run pip3 install sphinx
    run pip3 install sphinxcontrib.napoleon
    run pip3 install tachyonic-sphinx
    run python3 $src_path/setup.py develop

    run rm -rf $doc_dir
    run sphinx-build -c $virtualenv $src_path/docs/source $doc_dir
fi
