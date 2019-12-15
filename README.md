# ansible-config-merge
![build status](https://travis-ci.org/sshnaidm/ansible-config-merge.svg?branch=master)

Merge Ansible configuration files, taking into account appendable options

Run ```./ansible-config-merge.py /path/to/cfg1 /path/to/cfg2 /path/to/cfg3 ... > ansible-merged.cfg```
to get merged ansible configuration in `ansible-merged.cfg` file.
This tool combines and merges paths and lists from configurations instead of
overwriting them as usual `ansible-conifg` does.
