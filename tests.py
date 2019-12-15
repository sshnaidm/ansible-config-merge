#!/usr/bin/python3
import unittest
from io import StringIO


from ansible_config_merge import str_merge


def cfg2str(config_parser):
    cfg_io = StringIO()
    config_parser.write(cfg_io)
    cfg_io.seek(0)
    return cfg_io.read()


class TestConfigMerge(unittest.TestCase):

    def test_regular(self):
        cfg1 = """[defaults]
nonexist = 'some key'
bin_ansible_callbacks = True
stdout_callback = stdout
"""
        cfg2 = """[defaults]
bin_ansible_callbacks = False
stdout_callback = stdout
"""
        expected = """[defaults]
nonexist = 'some key'
bin_ansible_callbacks = False
stdout_callback = stdout

"""
        self.assertEqual(cfg2str(str_merge([cfg1, cfg2])), expected)

    def test_overwrite(self):
        cfg1 = """[defaults]
bin_ansible_callbacks = True
stdout_callback = stdout
nottouch = original
"""
        cfg2 = """[defaults]
bin_ansible_callbacks = False
stdout_callback = debug
oldkey = test1
[new]
newkey = test2
"""
        expected = """[defaults]
bin_ansible_callbacks = False
stdout_callback = debug
nottouch = original
oldkey = test1

[new]
newkey = test2

"""
        self.assertEqual(cfg2str(str_merge([cfg1, cfg2])), expected)

    def test_overwrite2(self):
        cfg1 = """[defaults]
set1 = value2
[newsec]
set2 = value3
[emptysec]
[dupsec]
"""
        cfg2 = """[defaults]
set2 = value3
[original]
set2 = value3
[dupsec]
nothing = here
"""
        expected = """[defaults]
set1 = value2
set2 = value3

[newsec]
set2 = value3

[emptysec]

[dupsec]
nothing = here

[original]
set2 = value3

"""
        self.assertEqual(cfg2str(str_merge([cfg1, cfg2])), expected)

    def test_overwrite3(self):
        cfg1 = """[defaults]
bin_ansible_callbacks = True
"""
        cfg2 = """[none]
[new]
newkey = test2
"""
        expected = """[defaults]
bin_ansible_callbacks = True

[none]

[new]
newkey = test2

"""
        self.assertEqual(cfg2str(str_merge([cfg1, cfg2])), expected)

    def test_single_appendable(self):
        cfg1 = """[defaults]
bin_ansible_callbacks = True
stdout_callback = stdout
connection_plugins = /home/ansible/plugins
"""
        cfg2 = """[defaults]
bin_ansible_callbacks = False
stdout_callback = debug
oldkey = test1
[new]
newkey = test2
"""
        expected = """[defaults]
bin_ansible_callbacks = False
stdout_callback = debug
connection_plugins = /home/ansible/plugins
oldkey = test1

[new]
newkey = test2

"""
        self.assertEqual(cfg2str(str_merge([cfg1, cfg2])), expected)

    def test_same_simple_appendable(self):
        cfg1 = """[defaults]
connection_plugins = /home/ansible/plugins
"""
        cfg2 = """[defaults]
oldkey = test1
connection_plugins = /home/ansible/plugins
"""
        expected = """[defaults]
connection_plugins = /home/ansible/plugins
oldkey = test1

"""
        self.assertEqual(cfg2str(str_merge([cfg1, cfg2])), expected)

    def test_combined_simple_appendable(self):
        cfg1 = """[defaults]
connection_plugins = /home/ansible/plugins
"""
        cfg2 = """[defaults]
connection_plugins = /plugins
"""
        expected = """[defaults]
connection_plugins = /home/ansible/plugins:/plugins

"""
        self.assertEqual(cfg2str(str_merge([cfg1, cfg2])), expected)

    def test_combined_appendable(self):
        cfg1 = """[defaults]
connection_plugins = /plugins:/tmp/plugins:/var/
"""
        cfg2 = """[defaults]
connection_plugins = /newplugins:/otherpath/path
"""
        expected = """[defaults]
connection_plugins = /plugins:/tmp/plugins:/var/:/newplugins:/otherpath/path

"""
        self.assertEqual(cfg2str(str_merge([cfg1, cfg2])), expected)

    def test_combined_same_appendable(self):
        cfg1 = """[defaults]
connection_plugins = /plugins:/tmp/plugins:/var:/otherpath/path
"""
        cfg2 = """[defaults]
connection_plugins = /plugins:/newplugins:/otherpath/path:/var
"""
        expected = """[defaults]
connection_plugins = /plugins:/tmp/plugins:/var:/otherpath/path:/newplugins

"""
        self.assertEqual(cfg2str(str_merge([cfg1, cfg2])), expected)

    def test_appendable_list(self):
        cfg1 = """[defaults]
connection_plugins = /plugins:/var:/otherpath/path
run = tag1, tag2, tag3
"""
        cfg2 = """[defaults]
oldkey = test1
connection_plugins = /plugins:/newplugins:/otherpath/path:/var:/plugins
"""
        expected = """[defaults]
connection_plugins = /plugins:/var:/otherpath/path:/newplugins
run = tag1, tag2, tag3
oldkey = test1

"""
        self.assertEqual(cfg2str(str_merge([cfg1, cfg2])), expected)

    def test_appendable_same_list(self):
        cfg1 = """[defaults]
connection_plugins = /var:/otherpath/path
run = tag1, tag2, tag3
"""
        cfg2 = """[defaults]
connection_plugins = /plugins:/newplugins:/otherpath/path:/var:/plugins
run = tag1, tag2, tag3
"""
        expected = """[defaults]
connection_plugins = /var:/otherpath/path:/plugins:/newplugins
run = tag1, tag2, tag3

"""
        self.assertEqual(cfg2str(str_merge([cfg1, cfg2])), expected)

    def test_appendable_combined_list(self):
        cfg1 = """[defaults]
connection_plugins = /var:/otherpath/path
run = tag1, tag2
"""
        cfg2 = """[defaults]
oldkey = test1
connection_plugins = /plugins:/newplugins:/otherpath/path:/var:/plugins
run = tag1, tag2, tag3
"""
        expected = """[defaults]
connection_plugins = /var:/otherpath/path:/plugins:/newplugins
run = tag1, tag2, tag3
oldkey = test1

"""
        self.assertEqual(cfg2str(str_merge([cfg1, cfg2])), expected)

    def test_appendable_combined_list2(self):
        cfg1 = """[defaults]
connection_plugins = /var:/otherpath/path
"""
        cfg2 = """[defaults]
connection_plugins = /plugins:/newplugins:/otherpath/path:/var:/plugins
run = tag1, tag2, tag3
"""
        expected = """[defaults]
connection_plugins = /var:/otherpath/path:/plugins:/newplugins
run = tag1, tag2, tag3

"""
        self.assertEqual(cfg2str(str_merge([cfg1, cfg2])), expected)

    def test_appendable_combined_list3(self):
        cfg1 = """[defaults]
connection_plugins = /var:/otherpath/path
run = tag1, tag2, tag3, tag5
"""
        cfg2 = """[defaults]
connection_plugins = /plugins:/newplugins:/otherpath/path:/var:/plugins
run = tag1, tag2, tag3, tag4
"""
        expected = """[defaults]
connection_plugins = /var:/otherpath/path:/plugins:/newplugins
run = tag1, tag2, tag3, tag5, tag4

"""
        self.assertEqual(cfg2str(str_merge([cfg1, cfg2])), expected)


if __name__ == '__main__':
    unittest.main()
