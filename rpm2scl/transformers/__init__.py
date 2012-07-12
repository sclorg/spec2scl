import os

files_in_transformers_dir = list(os.listdir(os.path.dirname(__file__)))
py_files_in_transformers_dir = filter(lambda x: x.endswith('.py'), files_in_transformers_dir)
modules_to_load = map(lambda x: x[:-3], py_files_in_transformers_dir)
modules_to_load.remove('__init__')
modules_to_load.remove('transformer')

for m in modules_to_load:
    __import__('{0}.{1}'.format(__package__, m))
