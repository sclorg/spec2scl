"""Package initialization.

Basically equivalent to:
from spec2scl.transformers import generic
from spec2scl.transformers import perl
from spec2scl.transformers import php
from spec2scl.transformers import python
from spec2scl.transformers import R
from spec2scl.transformers import ruby
"""

import importlib
import os

files_in_transformers_dir = list(os.listdir(os.path.dirname(__file__)))
py_files_in_transformers_dir = filter(lambda x: x.endswith('.py'), files_in_transformers_dir)
modules_to_load = list(map(lambda x: x[:-3], py_files_in_transformers_dir))
modules_to_load.remove('__init__')

for m in modules_to_load:
    importlib.import_module('{0}.{1}'.format(__package__, m))
