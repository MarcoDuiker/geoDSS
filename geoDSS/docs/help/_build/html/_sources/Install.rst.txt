=======
Install
=======

Before you start
----------------

geoDSS is written in Python. So you first need to install Python 2.x. Python 3.x support is yet to come.

Some processors or tests may require Python packages you don't have. Either omit using these tests and processors or install these dependencies.
Most probably that can be done by ``pip``.

At least you'll need the following Python packages:

- markdown
- requests
- yaml

Most off the time you'll also want to install:

- psycopg2
- json
- xml
- ogr

If you'd like to use the nice geospatial functions based on Postgis you'll need to install PostgreSQL/ Postgis and the Python package psycopg2.

Basic
-----

If you are lucky you can download a ``pip`` installable package from GitHub.

If so, you can simply install by typing in a terminal:

``pip install <downloaded_package>``

If pip is not installed on your system you can install pip by typing:

``easy_install pip``

On windows, ``easy_install`` and ``pip`` often are not recognised. If so, you'll find ``easy_install`` in the ``scripts`` folder of your Python installation. 

Advanced
--------

Clone the geoDSS repository from GitHub or download the zip and extract.

Then do:

``python setup.py build``

``python setup.py install``

Alternatively you can also create an installable first, and install that with ``pip``:

``python setup.py bdist_wheel``

And then do:

``pip install <the_wheel_file_you_created.whl>``


