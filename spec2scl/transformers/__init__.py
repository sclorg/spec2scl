"""Transformer plugins.

Each transformer plugin represents a collection of methods
decorated with `matches`, where the method is a handler
and performs transformation, and the decorator stores
regex patterns and specfile sections they should be applied to.

The base Transformer class is responsible for collecting
those methods and call them on a specfile.

To register a new plugin add a new file with a plugin class
which should inherit from base Transformer, register it
with `register_transformer` decorator and import here.
The base Transformer class will take care of the rest.
"""

from spec2scl.transformers.generic import GenericTransformer  # noqa
