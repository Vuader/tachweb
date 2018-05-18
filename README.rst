=========================
Tachyonic Project Website
=========================

This package is used internally for Tachyonic Project website. http://www.tachyonic.org

Install
-------

For updating the website install Tachyonic website on your machine in python virtual enviornment.

You will need to setup a virtual environment which requires virtualenv python package.

.. code:: bash

    $ pip3 install virtualenv
    $ virtualenv tachweb_venv
    $ source tachweb_venv/bin/activate

Secondly you need to clone 'tachweb' project and ensure your working on development branch

.. code:: bash

    $ git clone https://github.com/TachyonicProject/tachweb.git tachweb_repo
    $ cd tachweb_repo
    $ git checkout development

Once you have cloned it, you can install the tachweb package using:

.. code:: bash

    $ python3 setup.py develop

To deploy the Tachyonic project:

.. code:: bash

    $ cd .. # return to working directory containing tachweb_venv and tachweb_repo
    $ mkdir tachweb # create directory for deployment of tachweb luxon application
    $ luxon -i tachweb tachweb # instruct luxon to install 'tachweb' luxon package into tachweb
    $ luxon -d tachweb # instruct luxon to create 'tachweb' database (default sqlite3)

The Tachyonic website syncs all TachyonicProject Repositories, Events, Team members and Projects with GitHub. For this to work correctly, you will need to provide a valid GitHub account.

You will need to modify the 'tachweb/settings.ini' section [github]. Replace username and password with your valid github account. Ensure nobody can get to the settings.ini as it expoes your personal credentials.

Finally start Tachyonic Website
-------------------------------
At this point you can start website using built-in server with gunicorn:

.. code:: bash

    $ pip3 install gunicorn
    $ luxon -s tachweb

The website can be accessed by http://127.0.0.1:8080

Updating Website with GitHub information
----------------------------------------

You will notice that none of the documentation has been built and information sourced from github is missing. This task is given to backend process. You can run it like so:

.. code:: bash

    $ tachweb -a tachweb github sync
