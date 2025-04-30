#!/usr/bin/env bash

set -euo pipefail

POSITIONAL_ARGS=()

SKIP_INSTALL=NO
SKIP_POPULATE=NO

DEFAULT_PYTHON=python3

INDEX_LOCATION=""
INDEX_NAME="cosmic-local"

FORCE=NO

while [[ $# -gt 0 ]]; do
    case $1 in
        -il|--index-location)
            INDEX_LOCATION=$2
            shift # past argument
            shift # past value
            ;;
        -in|--index-name)
            INDEX_NAME=$2
            shift # past argument
            shift # past value
            ;;
        -si|--skip-install)
            SKIP_INSTALL=YES
            shift # past argument
            ;;
        -sp|--skip-populate)
            SKIP_POPULATE=YES
            shift # past argument
            ;;
        -f|--force)
            FORCE=YES
            shift # past argument
            ;;
        -p|--python)
            DEFAULT_PYTHON=$2
            shift # past argument
            shift # past value
            ;;
        -h|--help)
            echo "Usage: $0 [options]"
            echo "Options:"
            echo "  -il, --index-location <path>  Set the location of the index"
            echo "  -in, --index-name <name>      Set the name of the index"
            echo "  -si, --skip-install           Skip the conan install"
            echo "  -sp, --skip-populate          Skip the conan populate"
            echo "  -f, --force                   Force the download of the index"
            echo "  -p, --python <python>         Set the python executable to use"
            echo "  -h, --help                    Show this help"
            exit 0
            ;;
        -*|--*)
            echo "Unknown option $1"
            exit 1
            ;;
        *)
            POSITIONAL_ARGS+=("$1") # save positional arg
            shift # past argument
            ;;
    esac
done

if [[ ${#POSITIONAL_ARGS[@]} -gt 0 ]]; then
    set -- "${POSITIONAL_ARGS[@]}"
fi

#################
# CONAN INSTALL #
#################
if [[ "${SKIP_INSTALL}" == "NO" ]]; then
    echo "Installing conan…"

    # Install conan if not found
    command -v conan || $DEFAULT_PYTHON -m pip install conan

else
    echo -e "Skipping conan install…\n"
fi

# if index location is not set, use the default
if [[ -z $INDEX_LOCATION ]]; then
    conan_home=$(conan config home)

    INDEX_LOCATION=$conan_home/cosmic-local-index
fi

####################
# INDEX POPULATION #
####################
if [[ "${SKIP_POPULATE}" == "NO" ]]; then
    echo "Populating the index…"

    if [[ ! -d $INDEX_LOCATION ]] || [[ "$FORCE" == "YES" ]]; then
        rm -rf $INDEX_LOCATION
        echo "Downloading index to $INDEX_LOCATION"
        git clone https://github.com/raplonu/cosmic-center-index.git $INDEX_LOCATION --depth 1
    else
        echo -e "Index location $INDEX_LOCATION already exists. Use --force to overwrite"
    fi

    conan remote add -t local-recipes-index $INDEX_NAME $INDEX_LOCATION --force -verror

else
    echo -e "Skipping index populate…\n"
fi
