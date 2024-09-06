#!/usr/bin/env bash

set -euo pipefail

POSITIONAL_ARGS=()

SKIP_INSTALL=NO
SKIP_CONFIGURE=NO
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
        -sc|--skip-configure)
            SKIP_CONFIGURE=YES
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
            echo "  -sc, --skip-configure         Skip the conan configure"
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

set -- "${POSITIONAL_ARGS[@]}" # restore positional parameters
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

###################
# CONAN CONFIGURE #
###################
if [[ "${SKIP_CONFIGURE}" == "NO" ]]; then
    # Create the default conan profile
    conan profile detect --force

    conan_home=$(conan config home)

    # Remove the cppstd settings. It does not add any value.
    sed -i '/compiler.cppstd/d' $conan_home/profiles/default

    # Disable unit test by default for all packages. Test can be re-enabled on a per package basis using `-c tools.build:skip_test=False`
    grep -q 'tools.build:skip_test' $conan_home/global.conf || echo 'tools.build:skip_test = True' >> $conan_home/global.conf
else
    echo -e "Skipping conan configure…\n"
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

    python3 << END
from urllib.request import urlopen, urlretrieve
import cgi
import tarfile, yaml
from glob import glob
from pathlib import Path
import os, subprocess, shutil
import tempfile
import hashlib

try:
    import progressbar
    pbar = None

    def show_progress(block_num, block_size, total_size):
        global pbar
        if pbar is None:
            pbar = progressbar.ProgressBar(maxval=total_size)
            pbar.start()

        downloaded = block_num * block_size
        if downloaded < total_size:
            pbar.update(downloaded)
        else:
            pbar.finish()
            pbar = None

except ImportError:
    show_progress = None

def download_file(url):
    remotefile = urlopen(url)
    contentdisposition = remotefile.info()['Content-Disposition']
    _, params = cgi.parse_header(contentdisposition)
    dst_file_name = tempfile.mkdtemp()
    filename = Path(dst_file_name, params["filename"])

    print(f"Downloading…")

    urlretrieve(url, filename, show_progress)
    return filename

def check_sha256(file_name, expected):
    result = hashlib.sha256()
    with open(file_name, 'rb') as f:
        while data := f.read(65536):
            result.update(data)
    if result.hexdigest() != expected:
        raise ValueError(f"{file_name.name} sha256 verification failed.\n\tExpected: {expected},\n\tGot: {result.hexdigest()}")

def export_archive(file_name, name, user, channel):
    if (not user) and channel:
        raise ValueError(f'user needs to be specified if using channel.\n\tGot user: "{user}", channel: "{channel}"')

    dst_file_name = Path(tempfile.mkdtemp())

    os.makedirs(dst_file_name, exist_ok=True)

    # decompress the file
    with tarfile.open(file_name) as f:
        dst = os.path.commonprefix(f.getnames())
        f.extractall(dst_file_name)

    cmd = ["conan", "export", str(dst_file_name / dst), "--name", name]

    if user: cmd.extend(["--user", user])
    if channel: cmd.extend(["--channel", channel])

    subprocess.run(cmd, check=True)

    shutil.rmtree(dst_file_name)

def install_external_recipes():
    # for every conandata.yml file in 'external_recipes/*' folders
    for conandata_location in glob('external_recipes/*/conandata.yml'):
        name = conandata_location.split("/")[1]
        print(f'Adding \033[92m{name}\033[0m to the cache')
        # load the conandata.yml file
        with open(conandata_location) as f:
            conandata = yaml.safe_load(f)
        # for every source in the conandata.yml file
        for version, source in conandata['sources'].items():
            print(f'\tExporting version \033[92m{version}\033[0m')
            # download the source
            archive_file = download_file(source['url'])
            #check sha256 if present
            if 'sha256' in source:
                check_sha256(archive_file, source['sha256'])

            export_archive(archive_file, name, source.get('user'), source.get('channel'))
            # remove the source
            os.remove(archive_file)
            print()

if __name__ == '__main__':
    print("Installing external recipes…")
    try:
        install_external_recipes()
    except Exception as e:
        print(f"An error occurred:\n{str(e)}")
END

else
    echo -e "Skipping index populate…\n"
fi
