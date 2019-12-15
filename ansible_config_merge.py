#!/usr/bin/python3
import configparser
import os
import sys

from io import StringIO


APPENDABLES = {
    'collections_paths': 'pathspec',
    'doc_fragment_plugins': 'pathspec',
    'action_plugins': 'pathspec',
    'become_plugins': 'pathspec',
    'cache_plugins': 'pathspec',
    'callback_plugins': 'pathspec',
    'cliconf_plugins': 'pathspec',
    'connection_plugins': 'pathspec',
    'filter_plugins': 'pathspec',
    'httpapi_plugins': 'pathspec',
    'inventory_plugins': 'pathspec',
    'lookup_plugins': 'pathspec',
    'library': 'pathspec',
    'module_utils': 'pathspec',
    'netconf_plugins': 'pathspec',
    'roles_path': 'pathspec',
    'strategy_plugins': 'pathspec',
    'terminal_plugins': 'pathspec',
    'test_plugins': 'pathspec',
    'vars_plugins': 'pathspec',
    'cow_whitelist': 'list',
    'callable_whitelist': 'list',
    'callback_whitelist': 'list',
    'gather_subset': 'list',
    'log_filter': 'list',
    'special_context_filesystems': 'list',
    'squash_actions': 'list',
    'vault_identity_list': 'list',
    'facts_modules': 'list',
    'role_skeleton_ignore': 'list',
    'server_list': 'list',
    'enable_plugins': 'list',
    'inventory_ignore_extensions': 'list',
    'inventory_ignore_patterns': 'list',
    'network_group_modules': 'list',
    'dont_type_filters': 'list',
    'run': 'list',
    'skip': 'list',
    'vars_plugins_enabled': 'list',
    'precedence': 'list',
    'yaml_valid_extensions': 'list',
    'inventory': 'pathlist',
}


def appendable(option, value, old_value):
    if option not in APPENDABLES:
        return value
    if APPENDABLES[option] == 'pathspec':
        values = value.split(os.pathsep)
        old_values = old_value.split(os.pathsep)
    elif APPENDABLES[option] in ('list', 'pathlist'):
        values = value.split(',')
        old_values = old_value.split(',')
    else:
        raise Exception('Not supported type %s' % APPENDABLES[option])
    for v in values:
        if v not in old_values:
            old_values.append(v)
    if APPENDABLES[option] == 'pathspec':
        return os.pathsep.join(old_values)
    if APPENDABLES[option] in ('list', 'pathlist'):
        return ",".join(old_values)
    raise Exception('Not supported type %s' % APPENDABLES[option])


def files_merge(args):
    configs = []
    for arg in args:
        c = configparser.ConfigParser()
        if isinstance(arg, StringIO):
            c.read_file(arg)
        else:
            c.read(arg)
        configs.append(c)
    result_cfg = configs[0]
    for cfg in configs[1:]:
        for section in cfg.sections():
            if not result_cfg.has_section(section):
                result_cfg.add_section(section)
            for option, value in cfg.items(section):
                if not result_cfg.has_option(section, option):
                    result_cfg.set(section, option, value)
                else:
                    new_value = appendable(option, value, result_cfg.get(
                        section, option))
                    result_cfg.set(section, option, new_value)
    return result_cfg


def str_merge(args):
    strs = []
    for arg in args:
        cfg_io = StringIO()
        cfg_io.write(arg)
        cfg_io.seek(0)
        strs.append(cfg_io)
    return files_merge(strs)


def main():
    new_cfg = files_merge(sys.argv[1:])
    new_cfg_io = StringIO()
    new_cfg.write(new_cfg_io)
    new_cfg_io.seek(0)
    print(new_cfg_io.read())


if __name__ == '__main__':
    main()
