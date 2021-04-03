YOGA Image Optimizer
====================

**YOGA Image Optimizer** is a graphical user interface for `YOGA Image <https://github.com/wanadev/yoga>`_ that **optimizes JPEGs and PNGs**.

**THIS PROJECT IS WORK IN PROGRESS**, there is no public release available yet. 😊️

.. figure:: ./screenshot.png
   :alt: YOGA Image Optimizer screenshot


Limitations
-----------

As this is an early development version:

* Only JPEG and PNG are supported as input file. This will be improved in the future to allow opening any image format supported by `Pillow <https://pillow.readthedocs.io/en/stable/>`_.

* PNG Optimization is very, very, **VERY** slow due to too unbalanced ZoppfliPNG optimization options set by YOGA, this will be improved in the future.


Requirements
------------

* Python >= 3.7,
* YOGA >= 0.11.0,
* PyCairo,
* PyGObject >= 3. 36,


Install
-------

First, you will need to install some dependencies on your system. On Debian and Ubuntu this can be achieved with the following command::

    sudo apt install git build-essential python3 python3-dev python3-pip libgirepository1.0-dev libcairo2-dev pkg-config gir1.2-gtk-3.0

Then clone this repository::

    git clone https://github.com/flozz/yoga-image-optimizer.git
    cd yoga-image-optimizer

And install YOGA Image Optimizer::

    sudo pip3 install .


Usage
-----

To run YOGA Image Optimizer, just type the following command::

    yoga-image-optimizer

You can also pass some image files to open::

    yoga-image-optimizer  image1.png  image2.jpeg


Contributing
------------

Questions
~~~~~~~~~

If you have any question, you can:

* `open an issue <https://github.com/flozz/yoga-image-optimizer/issues>`_ on Github,
* or `ask on Discord <https://discord.gg/P77sWhuSs4>`_ (I am not always available for chatting but I try to answer to everyone).

Bugs
~~~~

If you found a bug, please `open an issue <https://github.com/flozz/yoga-image-optimizer/issues>`_ on Github with as much information as possible:

* What is your operating system / Linux distribution (and its version),
* How you installed the software,
* All the logs and message outputted by the software,
* ...

Pull Requests
~~~~~~~~~~~~~

Please consider `filing a bug <https://github.com/flozz/yoga-image-optimizer/issues>`_ before starting to work on a new feature. This will allow us to discuss the best way to do it. This is of course not necessary if you just want to fix some typo or small errors in the code.

Please note that your code must pass tests and follow the coding style defined by the `pep8 <https://pep8.org/>`_. `Flake8 <https://flake8.pycqa.org/en/latest/>`_ and `Black <https://black.readthedocs.io/en/stable/>`_ are used on this project to enforce coding style.

Running The Tests
~~~~~~~~~~~~~~~~~

You will first have to install `nox <https://nox.thea.codes/>`_::

    pip3 install nox

Then you can check for lint error::

    nox --session lint

or run the tests::

    nox --session test

You can also fix automatically coding style errors with::

    nox -s black_fix

To run the tests only for a specific Python version, you can use following commands (the corresponding Python interpreter must be installed on your machine)::

    nox --session test-3.7
    nox --session test-3.8
    nox --session test-3.9
