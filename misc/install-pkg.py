
'''
This script is the reference implementation for installing external pkgs in the conan cache in the `install.sh` script.
We recommend using the `install.sh` script instead of this script. If you want to use this script, you can run it from the root of the repository.
Modification of this script should be repercuted in the `install.sh` script.
'''

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

def export_archive(file_name, name, version):
    dst_file_name = Path(tempfile.mkdtemp())

    os.makedirs(dst_file_name, exist_ok=True)

    # decompress the file
    with tarfile.open(file_name) as f:
        dst = os.path.commonprefix(f.getnames())
        f.extractall(dst_file_name)

    subprocess.run(["conan", "export", str(dst_file_name / dst)])

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

            export_archive(archive_file, name, version)
            # remove the source
            os.remove(archive_file)
            print()

if __name__ == '__main__':
    print("Installing external recipes…")
    try:
        install_external_recipes()
    except Exception as e:
        print(f"An error occurred:\n{str(e)}")
