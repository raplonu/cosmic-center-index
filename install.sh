#!/usr/bin/env bash

set -Eeuo pipefail
umask 022

POSITIONAL_ARGS=()

DO_INSTALL=NO

DEFAULT_PYTHON=python3

INDEX_LOCATION=""
INDEX_NAME="cosmic-local"

FORCE=NO

archive_url="https://github.com/raplonu/cosmic-center-index/archive/refs/heads/main.tar.gz"

while [[ $# -gt 0 ]]; do
    case $1 in
        -l|--index-location)
            INDEX_LOCATION=$2
            shift # past argument
            shift # past value
            ;;
        -n|--index-name)
            INDEX_NAME=$2
            shift # past argument
            shift # past value
            ;;
        -i|--install)
            DO_INSTALL=YES
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
            echo "  -l, --index-location <path>   Set the location of the index (default: <conan_home>/cosmic-local-index)"
            echo "  -n, --index-name <name>       Set the name of the index (default: cosmic-local)"
            echo "  -i, --install                 Install conan (default: NO)"
            echo "  -f, --force                   Force the download of the index (default: NO)"
            echo "  -p, --python <python>         Set the python executable to use (default: python3)"
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
if [[ "${DO_INSTALL}" == "YES" ]]; then
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
echo "Populating the index…"

if [[ ! -d $INDEX_LOCATION ]] || [[ "$FORCE" == "YES" ]]; then
    rm -rf $INDEX_LOCATION
    echo "Downloading index to $INDEX_LOCATION"
    # Download the repo archive and extract it to the index location
    tmp_dir="$(mktemp -d)"
    trap 'rm -rf "$tmp_dir"' EXIT

    staging="$tmp_dir/staging"
    mkdir -p "$staging"

    # Stream + extract, don’t depend on repo-name folder; include dotfiles
    curl -fsSL --retry 3 --retry-connrefused --connect-timeout 10 "$archive_url" \
    | tar -xz -C "$staging" --strip-components=1 --no-same-owner

    # Mirror to destination (preserve perms, include dotfiles, remove deleted files)
    rsync -a --delete "$staging"/ "$INDEX_LOCATION"/
else
    echo -e "Index location $INDEX_LOCATION already exists. Use --force to overwrite"
fi

conan remote add -t local-recipes-index $INDEX_NAME $INDEX_LOCATION --force -verror
