from rpm2scl.decorators import matches
from rpm2scl.transformers.transformer import Transformer

class RubyTransformer(Transformer):
    def __init__(self, spec, options = None):
        super(RubyTransformer, self).__init__(spec, options)

    @matches(r'gem (?:(?:install)|(?:unpack)|(?:build))', one_line = False)
    @matches(r'testrb ', one_line = False)
    @matches(r'testrb2 ', one_line = False)
    @matches(r'(?<!-)rspec ', one_line = False) # avoid matching stuff like 'rubygem-rspec ' here
    def handle_ruby_specific_commands(self, pattern, text):
        print pattern.search(text).groups()
        return self.sclize_all_commands(pattern, text)
