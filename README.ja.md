# ansiblerole2sphinx
ansible-galaxy で初期化された role を前提に、その ansibleの playbook から sphinx用のテンプレートとなる rst ファイルを吐き出します。

# 使い方

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

## サンプル

   $ ./ansiblerole2sphinx.py common -s ~/Documents/devel/ansible/roles -d ~/Documents/devel/sphinx-doc/source/ansible

上記を実行すると、

- ~/Documents/devel/ansible/roles/common/tasks/main.yml から、タスク一覧の生成
- ~/Documents/devel/ansible/roles/common/handlers/main.yml から Notify一覧の生成
- ~/Documents/devel/ansible/roles/common/defaults/main.yml から変数一覧の生成

などを行います。その結果  ~/Documents/devel/sphinx-doc/source/ansible 以下に

```
├── common
│   ├── summary.rst
│   ├── tasks_desc_1.rst
│   ├── tasks_desc_2.rst
│   ├── tasks_desc_3.rst
│   └── tasks_desc_4.rst
└── common.rst
```

のような形式でファイルを書き出します。

- tasks_desc_1.rst 

のように連番で吐き出されているファイルとタスクとが待避しており、このファイルは以降上書きされません。このためroleでは書けないタスクの詳細を手動で書き出すことが可能です。role 自体の説明は summary.rst に書いてください。これらは {ロール名}.rst、今回の例だと、common.rst から include されます。

なお、conf.py には

```
def setup(app):
    app.add_object_type('ansibleval', 'ansibleval',
                        objname='ansible configuration value',
                        indextemplate=u'pair: %s; Ansible設定値')
```

を書いておく必要があります。これは変数一覧での表示に利用します。これを定義することで、予備がしている変数を元にした索引が生成されます。


## 出力サンプル

- https://github.com/kunitake/ansible-crowi/tree/sphinx-doc/sphinx-doc


