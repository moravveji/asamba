# ASAMBA: Asteroseismic Modelling Database Python Tools

[TOC]

## About
The `asamba` is a Python interface to interact with the forward asteroseismic grid of massive stars, computed by the MESA stellar structure and evolution code, coupled with the GYRE adiabatic nonradial pulsation code. The whole data in the grid is organized as a PostgreSQL database, and the `asamba` module allows the users to exploit this database.

The computation of the grid, the development of the database, and the development of this repository are currently under intense development. So, things will grow/improve steeply soon.

## Installation
... of `asamba` is pretty easy! There are variety of possibilities to download and install this repository on your local machine. But below, I mention two of the most straightforward approaches:

* (Recommended) The `asamba` is rolled as a package, and is officially released through the Python Package Index (PyPI). You may access the package via this link <https://pypi.python.org/pypi/asamba/1.02>. Therefore, you can use the `pip` command. 

```bash
pip install asamba 
```

If you require `sudo` permission to install the package, and you only have the user rights on your local machine, you have two options to install the repository: (1) installing as a user, or (2) directing the installation to a user-specified directory.

(1) To install the package on any user-defined target directory, say `<target-dir>` (absolute path), you do the following:

```bash
pip install --user asamba 
```

The reason for adding the `--user` argument is to ensure the user can fetch the repository even if they do not have the admin permission. 

(2) If you like to direct the download/extraction of the package into a specific target directory on your local machine, say `<target-dir>`, you may do the following instead.

```bash
pip install --user -b <target-dir> asamba 
```

Then, you will find a new folder in the following path `<target-dir>/asamba`. The `-b` directs the downloading and the building of the repository to the absulute path `<target-dir>`.

* Alternatively, you can clone the repository directly through the github host page as

```bash
cd <target-dir>
git clone git@github.com:moravveji/asamba.git
cd asamba
touch __init__.py
```
Note the double-underscores around the name of the `__init__.py` file. The next step is to add the full (absolute) path to the new directory to your `PYTHONPATH` environment variable. For that purpose, open your `~/.bash_profile`, and add the following line somewhere there.

```bash
vim ~/.bash_profile
export PYTHONPATH=$PYTHONPATH:<target-dir>/asamba
```

Then, you save changes in your `~/.bash_profile`, and `source` the `~/.bash_profile` file

```bash
source ~/.bash_profile
```

Basically, you must be able now to use the repository. To test that you can successfully import the package, please run the following line in your command line, and it shall exit silently, wihout any error/output message, in which case you have successfully installed the `asamba` package.

```bash
python -c 'import asamba'
```

If your installation/import fails, please contact me.

## Documentation
All modules and functions in the repository are documented. Thus, it is easy to read the intent of each module/function/class objects, by referring to the source code. An alternative way to read the basic documentation of the class objects is to instantiate them, and then accessing the `__doc__` attribute. As an example, to read the documentation for the `model` object, one can do the following:

```python
from asamba import var_def
a_model = var_def.model()
print a_model.__doc__
```
Soon, an HTML documentation page will be also added to the repository for a more convenient representation of the entire documented modules, functions and classes.

## Notes About The Data Structure
Below, I provide few key notes about how the data is organized in this package.

* The attribute names of the `model` classe is borrowed from their exact names in the MESA output history file. These names also match the attributes of the database table `models`. Therefore, MESA users have easy time understanding the meaning of the data in the database/repository.

* The physical units of all variables follow closely their units in MESA. E.g. the initial mass is given in solar unit, while the temperature (and other quantities) is given in CGS units. Thus, a proper reference to figure out the unit of each parameter is by consulting the `<mesa>/star/defaults/history_columns.list` file.

## The Query Syntax: Approximately Equals to
Except the row IDs of all tables, the rest of the attributes across the whole database are single-precision (i.e. of type `real` in SQL). As a result, the *floating point round-off does abandon retrieval of rows by providing the input attributes* (e.g. to retrieve the id of a row of the "tracks" table by providing M_ini, fov, Z and logD). This means that a basic SQL query like the following is so volunerable to fail, and doomed to return no result:

```SQL
SELECT id FROM grid.tracks WHERE M_ini = 12.345 AND fov = 0.012 AND Z = 0.014 AND logD = 02.34;
```

Something should be done about the equality comparison operation (i.e. `=`). As a work around, a new operator is overloaded, to represent *approximately equals to*, and it is represented by the tilde symbol **~**. The check for this near-equality is performed within the single floating point precision, i.e. **10^{-5}**. Two values are approximately equal to one another if their *relative absolute difference* is less than ten parts in million. In simple math terms:

<img src="http://www.sciweavers.org/tex2img.php?eq=a%5Csimeq%20b%20%5Cquad%20%7B%5Crm%20if%7D%20%5Cquad%20%7Ca-b%7C%20%5Cleq%2010%5E%7B-5%7D%20%7Ca%7C&bc=White&fc=Black&im=jpg&fs=12&ff=arev&edit=0" align="center" border="0" alt="a\simeq b \quad {\rm if} \quad |a-b| \leq 10^{-5} |a|" width="226" height="21" />

To enjoy this convenience operation, one needs to use the tilde operator *~* instead of the equality sign in the SQL `WHERE` clauses. Therefore, the following SQL query syntax works instead:

```SQL
SELECT id FROM grid.tracks WHERE M_ini ~ 12.345 AND fov ~ 0.012 AND Z ~ 0.014 AND logD ~ 02.34;
```

I strongly recommend users towards exploiting this overloaded `~` operator.

## References