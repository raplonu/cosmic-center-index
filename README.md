# Cosmic center index <img align="right" width="10%" src="assets/cosmic.png">

Cosmic Center Index is the source index of recipes of the [Cosmic](https://cosmic.pages.obspm.fr/cosmic/) package repository for [Conan](https://conan.io).

## Installation

`conan` is a package manager for C and C++ projects. It is designed to be portable and extensible, allowing you to install and manage dependencies for your projects.

The repository comes in two flavors:

> Note: It is totally fine to use both at the same time. `conan` will always try to find a matching binary package first and will then fallback to building its own using the recipe provided by one of the remotes (the first in the remote list).

### Recommended: Conan gitlab repository 🌐

To add it:

```bash
conan remote add cosmic https://gitlab.com/api/v4/projects/81598098/packages/conan
```

This instance will host all release versions of Cosmic's projects as well as pre-release and development version.

### Legacy/backup: Conan local repository 🛖

In addition of the server instance, we also maintain a conan local registry which can be cloned and referenced by conan. The repository will only reference release version of the cosmic packages.

> Note: This repository only contains the recipes. The user will have to compiles the packages in order to use them using the conan flag `-b missing`.

We offer a script to streamline the installation of Conan and the setup of the Cosmic repository. This script will install the conan cosmic repository.

```bash
curl -sS https://raw.githubusercontent.com/raplonu/cosmic-center-index/refs/heads/main/install.sh | bash
```

The script accepts additional arguments:

```bash
Options:
  -l, --index-location <path>   Set the location of the index (default: <conan_home>/cosmic-local-index)
  -n, --index-name <name>       Set the name of the index (default: cosmic-local)
  -i, --install                 Install conan (default: NO)
  -f, --force                   Force the download of the index (default: NO)
  -p, --python <python>         Set the python executable to use (default: python3)
  -h, --help                    Show this help
```

```bash
# Install conan 🐸 and override the repository 🖊️
curl -sS https://raw.githubusercontent.com/raplonu/cosmic-center-index/refs/heads/main/install.sh | bash -s -- --install --force
```

## Add Cosmic Center Index (WIP)

If you have already cloned the repository, you can add the Cosmic Center Index to your local Conan configuration by running:

```bash
conan remote add cosmic-local <path-to-cosmic-center-index-folder>
```

> Since it is a local repository, you will need to pull the latest changes from the remote repository to keep it up to date.

## How to consume recipes

Starting to use recipes from this repository is as easy as running
one simple command after installing Conan:

```bash
conan install name/version@ [-g <generator>]
```

Of course, we really encourage you to use a `conanfile.txt` or `conanfile.py`
to list all the requirements or your project and install them all together
(Conan will build a single graph and ensure congruency).

You can start with a simple `conanfile.txt` next to your `CMakeLists.txt` with the following content:

```toml
[requires]
fmt/12.1.0

[generators]
CMakeDeps
CMakeToolchain

[layout]
cmake_layout
```

Then type the following command:

```bash
conan install . -b missing
```

This command will pull, compile, and generate the necessary integration files (such as CMake toolchain and find-module files) to locate the dependencies on your local machine. It also will create cmake presets that can be listed using:

```bash
cmake --list-presets
```

By default, conan's presets have a `conan-` prefix.

:warning: It is very important to notice that recipes will evolve over time
and, while they are fixing some issues, they might introduce new features and
improvements, and your project can break if you upgrade them
([How to prevent these breaking changes in my project?](docs/consuming_recipes.md)).

## Documentation

`conan` documentation is available at [https://docs.conan.io](https://docs.conan.io/2/).

All the documentation is available in this same repository in the [`docs/` subfolder](docs/README.md).

This is a list of shortcuts to some interesting topics:

* :rocket: If you want to learn how to **contribute new recipes**, please read [docs/adding_packages/](docs/adding_packages/README.md).
* :speech_balloon: **FAQ**: most common questions are listed in [docs/faqs.md](docs/faqs.md).
* :warning: The conan-center **hook errors** reported by CCI Bot can be found in the [docs/error_knowledge_base.md](docs/error_knowledge_base.md).
* :hammer_and_wrench: The internal changes related to infrastructure can be checked in [docs/changelog.md](docs/changelog.md).
* :world_map: There are various community lead initiatives which are outlined in [docs/community_resources.md](docs/community_resources.md).
* :magic_wand: To start preparing your recipes for **Conan 2.0**, please check [docs/v2_migration.md](docs/v2_migration.md).

## Reporting Issues

You can open issues in the [issue tracker](https://github.com/conan-io/conan-center-index/issues) to:

* :bug: Report **bugs/issues** in a package:
    - Use the `[package]` tag in the title of the issue to help identifying them.
    - If you detect any issue or missing feature in a package, for example, a build failure or a recipe that not support a specific configuration.
    - Specify the name and version (`zlib/1.2.11`) and any relevant details about the fail configuration: Applied profile, building machine...

* :bulb: Request a **new library** to be added:
    - Use the `[request]` label to search the library in the issue tracker in case it was already requested.
    - If not, use the same `[request]` tag in the title of the issue to help identifying them.
    - Indicate the name and the version of the library you would like to have in the repository. Also links to the project's website,
      source download/repository and in general any relevant information that helps creating a recipe for it.

*  :robot: Report **a failure** in the CI system:
    - If you open a Pull Request and get an unexpected error you might comment in the failing PR.
    - If the service or repository is down or failing, use the `[service]` tag in the title of a new issue to help identifying them.

If your issue is not appropriate for a public discussion, please contact us via e-mail at `info@conan.io`. Thanks!


## License

All the Conan recipes in this repository are distributed under the [MIT](LICENSE) license. There
are other files, like patches or examples used to test the packages, that could use different licenses,
for those files specific license and credit must be checked in the file itself.
