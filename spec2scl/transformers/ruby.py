from spec2scl import settings
from spec2scl import transformer
from spec2scl.decorators import matches


@transformer.Transformer.register_transformer
class RubyTransformer(transformer.Transformer):
    def __init__(self, options={}):
            super(RubyTransformer, self).__init__(options)

    @matches(r'(?<!y)gem\s+(?:(?:install)|(?:unpack)|(?:build)|(?:spec))',
             one_line=False,
             sections=settings.RUNTIME_SECTIONS)  # not to match string like "rubygem install"
    @matches(r'%gem_install\s*', one_line=False, sections=settings.RUNTIME_SECTIONS)
    @matches(r'^\s*ruby\s+', one_line=False, sections=settings.RUNTIME_SECTIONS)
    @matches(r'testrb\s+', one_line=False, sections=settings.RUNTIME_SECTIONS)
    @matches(r'testrb2\s+', one_line=False, sections=settings.RUNTIME_SECTIONS)
    @matches(r'(?<![-.])rspec\s+', one_line=False, sections=settings.RUNTIME_SECTIONS)
    def handle_ruby_specific_commands(self, original_spec, pattern, text):
        return self.sclize_all_commands(pattern, text)
