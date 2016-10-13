# ansiblerole2sphinx
Generate sphinx-doc template from ansible role file.

# Usage

```
$ ./ansiblerole2sphinx.py -h
usage: ansiblerole2sphinx.py [-h] [-v] [-s [path to ansible roles directory]]
                             [-d [path to sphinx-doc directory]]
                             rolename

Generate sphinx-doc template from ansible role file.

positional arguments:
  rolename              a rolename of ansible.

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  -s [path to ansible roles directory]
                        Directory path for ansbile roles
  -d [path to sphinx-doc directory]
                        Directory path for sphinx-doc
```

## Example

   $ ./ansiblerole2sphinx.py common
