
'''
This script is the reference implementation for installing external pkgs in the conan cache in the `install.sh` script.
We recommend using the `install.sh` script instead of this script. If you want to use this script, you can run it from the root of the repository.
Modification of this script should be repercuted in the `install.sh` script.
'''

from urllib.request import urlretrieve
import yaml
from glob import glob
from pathlib import Path
import os, subprocess, shutil
import tempfile
import hashlib
import requests

try:
    import progressbar
    pbar = None

    def show_progress(block_num, block_size, total_size):
        global pbar
        if pbar is None:
            pbar = progressbar.ProgressBar(maxval=total_size if total_size > 0 else progressbar.UnknownLength)
            pbar.start()

        downloaded = block_num * block_size
        if total_size > 0 and downloaded < total_size:
            pbar.update(downloaded)

    def show_progress_finish():
        global pbar
        pbar.finish()
        pbar = None

except ImportError:
    show_progress = None

    def show_progress_finish():
        ...

def download_file(url: str, filename: str = None) -> str:
    """
    Downloads a file from the given URL, using the provided filename if available.
    If the filename is not provided, attempts to derive it from the HTTP headers or URL path.

    Args:
        url (str): The URL of the file to download.
        filename (str, optional): The filename to use for the downloaded file. Defaults to None.

    Returns:
        str: The path to the downloaded file in a temporary directory.

    Raises:
        ValueError: If filename cannot be determined.
        RuntimeError: If file download fails.
    """
    if filename is None:
        # Attempt to get the filename from the Content-Disposition header
        response = requests.head(url, allow_redirects=True)
        if 'Content-Disposition' in response.headers:
            content_disposition = response.headers['Content-Disposition']
            if 'filename=' in content_disposition:
                filename = content_disposition.split('filename=')[-1].strip('"')

        # If no filename in headers, derive it from the URL path
        if not filename:
            parsed_url = urlparse(url)
            filename = os.path.basename(parsed_url.path)

        # If still no filename, raise an error
        if not filename:
            raise ValueError("Cannot determine filename from URL or headers.")

    # Create a temporary directory
    temp_dir = tempfile.mkdtemp()

    # Construct the full path for the file in the temporary directory
    file_path = os.path.join(temp_dir, filename)

    # Download the file
    urlretrieve(url, file_path, show_progress)

    show_progress_finish()

    return file_path

def check_sha256(file_name, expected):
    result = hashlib.sha256()
    with open(file_name, 'rb') as f:
        while data := f.read(65536):
            result.update(data)
    if result.hexdigest() != expected:
        raise ValueError(f"{file_name.name} sha256 verification failed.\n\tExpected: {expected},\n\tGot: {result.hexdigest()}")

def export_archive(file_name, name, user, channel):
    print(f'Got file: {file_name}, name: {name}, user: {user}, channel: {channel}')
    if (not user) and channel:
        raise ValueError(f'user needs to be specified if using channel.\n\tGot user: "{user}", channel: "{channel}"')

    dst_file_name = Path(tempfile.mkdtemp())

    os.makedirs(dst_file_name, exist_ok=True)

    # decompress the file
    shutil.unpack_archive(file_name, dst_file_name)

    dirs = os.listdir(dst_file_name)
    # If extract result in a unique directory, it is consider the root.
    package_root_dir = dst_file_name / dirs[0] if len(dirs) == 1 else dst_file_name

    cmd = ["conan", "export", str(package_root_dir), "--name", name]

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
            archive_file = download_file(source['url'], source.get('filename'))
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
