# Hanzi Link Database

This project aims to provide a simple Web query interface for various databases concerning Hanzi (Han ideographs / Chinese characters), such as Unihan, to show the links or connections between Hanzi, and eventually to help with constructing the author's own database of Hanzi with categorization for ease of learning and indexing.

## Usage

You need Python 2.7 with VirtualEnv to install and run. Sample procedures:

    cd $project-directory
    git submodule update --init
    virtualenv venv
    . venv/bin/activate
    pip install -r requirements.txt # some libraries rely on system packages. fix denpendencies first.
    python main.py

## License

This project is licensed under the terms of the GNU General Public License version 3 ([GPLv3](https://www.gnu.org/licenses/gpl-3.0.html)).

The author's [database](Database.md) affiliated with this project has another Creative Commons Attribution 4.0 license ([CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/)).

Licenses of third-party materials follow their terms respectively. Specifically, the Unihan database is distributed under [Unicode, Inc. License](http://www.unicode.org/copyright.html), and the text under CHISE and CJKVI projects follow GPLv2 or MIT license (see their project pages for details).
