from rpm2scl.decorators import matches
from rpm2scl.transformers.transformer import Transformer

class RubyTransformer(Transformer):
    def __init__(self, spec, options = None):
        super(RubyTransformer, self).__init__(spec, options)

    @matches(r'(?<!y)gem\s+(?:(?:install)|(?:unpack)|(?:build))', one_line = False) # not to match string like "rubygem install"
    @matches(r'testrb\s+', one_line = False)
    @matches(r'testrb2\s+', one_line = False)
    @matches(r'(?<!-)rspec\s+', one_line = False) # avoid matching stuff like 'rubygem-rspec ' here
    def handle_ruby_specific_commands(self, pattern, text):
        return self.sclize_all_commands(pattern, text)
