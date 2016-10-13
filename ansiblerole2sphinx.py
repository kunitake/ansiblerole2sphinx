#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Apache v2 License
#
# Author: KUNITAKE Koichi
#  
import os
import yaml
import argparse
import sys, codecs
sys.stdout = codecs.getwriter("utf-8")(sys.stdout)

#
# Editable values
#
default_src_dir = '~/Documents/devel/ansible/roles'
default_dst_dir = '~/Documents/devel/sphinx-doc/source/ansible'

#
prompt = '[yes/no]: '

parser = argparse.ArgumentParser(description='Generate sphinx-doc template from ansible role file.')
parser.add_argument('-v','--version', action='version', version='%(prog)s 0.1')
parser.add_argument('rolename', action='store', \
                    nargs=None, \
                    const=None, \
                    default=None, \
                    type=str,\
                    choices=None, \
                    metavar=None, \
                    help='a rolename of ansible.')

parser.add_argument('-s', \
        action='store', \
        nargs='?', \
        const=None, \
        default=default_src_dir, \
        type=str, \
        choices=None, \
        help='Directory path for ansbile roles', \
        metavar="path to ansible roles directory")

parser.add_argument('-d', \
        action='store', \
        nargs='?', \
        const=None, \
        default=default_dst_dir, \
        type=str, \
        choices=None, \
        help='Directory path for sphinx-doc', \
        metavar="path to sphinx-doc directory")

args = parser.parse_args()

ansible_roles_dir = args.s

rolename = args.rolename
sphinx_output_dir = args.d
sphinx_desc_output_dir = sphinx_output_dir + "/" + rolename

if not os.path.isdir(sphinx_desc_output_dir):
  os.mkdir(sphinx_desc_output_dir)

value_yaml_file = ansible_roles_dir + "/" + rolename + "/defaults/main.yml"
if os.path.isfile(value_yaml_file):
  value_data = yaml.load(file(value_yaml_file))

item_keys = ['when', 'condition', 'become', 'sudo', 'delegate_to', 'host', 'run_once', 'run once', 'tags', 'name', 'with_items', 'notify', 'register', 'environment', 'vars', 'gather_facts', 'ignore_errors','vars_files','remote_user', 'roles', 'with_nested', 'debug','with_dict', 'with_file', 'with_fileglob','with_together','with_subelements','with_sequence','with_random_choice','until','retries','delay','with_first_found','with_lines','with_indexed_items','with_ini','with_flattened','with_inventory_hostnames','loop_control','become_user']

def get_modulename(original, removekeys, default=None):
  return dict([ (k, original.pop(k, default)) for k in removekeys])

def section_level(title,level=1):
  # level must be less than 9.
  marks = ('#', '-', '^', '"')
  (index, type) = divmod(level-1, 2)

  magic_number = 2
  length = len(title.encode('utf-8')) + magic_number

  if type == 0:
    line = marks[index] * length
    result = "%s\n%s\n%s\n" % (line, title, line)
  if type == 1:
    line = marks[index] * length
    result = "%s\n%s\n" % (title, line)
 
  return result

def make_line(item):
    results = []
    if(isinstance(item, dict)):
        for key in item.keys():
           if (isinstance( item[key], list)):
               results.append(key + "=" + str(item[key][0]) )
           else:
               results.append(key + "=" + item[key])
    if(isinstance(item, list)):
        for a in item:
            results.extend(make_line(a))
    if(isinstance(item, str)):
        results.append("    " + item + "\n")
    return results

def get_tasklist(mode, targetfile='main.yml',count=0, depth=3):
    yaml_file = ansible_roles_dir + "/" + rolename + "/" + mode + "/" + targetfile
    task_list = []
    results = []
    if os.path.isfile(yaml_file):
        data = yaml.load(file(yaml_file))
        if data is None:
            return task_list, results, count

        for task in data:
            # FIXME: When I get a list greater than 1?
            subset = get_modulename(task, item_keys)
            task_reference = mode + "_" + rolename + "_" + str(count)

            value = task.values()
            module_name = task.keys()

            # It is conceivable that it does not include 'name' and so-on.
            # Example:
            # - include: common-packages.yml
            # - include: mongo.yml
            if len(task) == 1 and module_name[0] == 'include':
                (include_list, include_results, count) = get_tasklist('tasks', targetfile=value[0], count=count+1, depth=depth)
                task_list.extend(include_list)
                results.extend(include_results)
                continue

            # Make an index for module name.
            results.append(".. index::")
            results.append("    single: " + module_name[0] + "; " + subset['name'] + "\n")

            # make a reference for task list.
            task_list.append('- :ref:`' + task_reference + '`')
            results.append(".. _" + task_reference + ":\n")

            # make the section by task name.
            results.append(section_level(subset['name'],level=depth))

            # task name by admonition form.
            # It's same name as section name, it is verbose...
            results.append(".. admonition:: " + subset['name'] + "\n")

            # make an argument line of the module.
            argument_of_module = ''
            for a in make_line(value[0]):
                argument_of_module = argument_of_module + " " + a
            results.append("    " + argument_of_module)

            # for module name.
            results.append(" " * 4 +  ":module: " + module_name[0])

            # list items exclude ansible task module and name part from the item list.
            for key in item_keys:
                if key == 'name':
                   continue
                if (isinstance(subset[key], str)):
                    if key == 'notify':
                        subset[key] = subset[key].replace(' ', '_')
                        results.append(" " * 4 + ":" + key + ": :ref:`" + subset[key] + '`' )
                    else:
                        results.append(" " * 4 + ":" + key + ": " + subset[key] )
                if (isinstance(subset[key], list)):
                    results.append(" " * 4 + ":" + key + ":")
                    #results.extend(expand_list(subset[key], 1))
                    for item in subset[key]:
                        results.append(" " * 5 + "- " + item)

            results.append("\n")

            desc_file = rolename + "/" + mode + "_desc_" + str(count) + ".rst"
            if not os.path.isfile(sphinx_output_dir + "/" + desc_file):
                f = open(sphinx_output_dir + "/" + desc_file , "w")
                f.write(".. " + subset['name'].encode('utf-8'))
                f.close
            results.append(".. include:: " + desc_file)

            if module_name[0] == 'include':
               (include_list, include_results, count) = get_tasklist('tasks', targetfile=value[0], count=count+1, depth=depth+1)
               task_list.extend(include_list)
               results.extend(include_results)
           
            results.append("\n")
            count = count + 1
        return task_list, results, count - 1

(task_list, results, count) = get_tasklist('tasks')


##
## output rst files
##
def print_ansibleval():
    print ""
    print "    def setup(app):"
    print "    app.add_object_type('ansibleval', 'ansibleval','"
    print "                        objname='ansible configuration value',"
    print u"                        indextemplate=u'pair: \%s; Ansible設定値')"
    print ""


role_file = rolename + ".rst"
writable = 0
if not os.path.isfile(sphinx_output_dir + "/" + role_file):
    writable = 1 
else:
    print "The rolename file(%s) already exists. Do you want to overwrite it?" % role_file
    overwrite = raw_input(prompt)
    if overwrite == 'yes':
        writable = 1

# Basically, a summary file is edited by author.
# So, the summary file is not overwrited.
summary_file = rolename + "/" + "summary.rst"
if not os.path.isfile(sphinx_output_dir + "/" + summary_file):
    print "  .. %s" % summary_file
    f_summary = open(sphinx_output_dir + "/" + summary_file , "w")
    f_summary.write(".. summary")
    f_summary.close

if writable == 1:
    f = open(sphinx_output_dir + "/" + role_file , "w")
    f.write(".. include:: ansible-variables.txt\n\n")
    f.write(".. _ansible-roles-" + rolename + ":\n\n")

    f.write(section_level(rolename + " role" ,level=1).encode('utf-8'))

    f.write(".. include:: " + summary_file + "\n\n")
    f.write(section_level(u"タスク一覧" ,level=2).encode('utf-8'))
    f.write("\n")

    for task in task_list:
       f.write(task + "\n")

    for line in results:
        f.write(line + "\n")

    if 'value_data' in locals():
        print "Please check/update ansible-variables.txt"
        print "Please define ansibleval at conf.py."
        print_ansibleval()
        f.write(section_level(u"変数" ,level=2).encode('utf-8'))
        for value in value_data:
            f.write(".. ansibleval:: " + value + "\n\n")
            f.write("  |" + value + "|\n\n")

    (handler_list, results, count) = get_tasklist('handlers')
    if len(handler_list) > 0:
        f.write(section_level(u"Notify一覧" ,level=2).encode('utf-8'))
        for handler in handler_list:
            f.write(handler + "\n")
    for line in results:
        f.write(line + "\n")
    f.close
