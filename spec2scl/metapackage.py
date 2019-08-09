"""SCL metapackge related data.

Used by CLI command to produce a spec file for SCL metapackage.
"""

from __future__ import unicode_literals

import jinja2
import locale
import re
import subprocess
import time


class Metapackage(object):

    """Class MetaPackage provides necessary informations
    to create a specfile for metapackage.
    """

    def __init__(self, meta_name, variables=None):
        self._meta_name = meta_name
        self._variables = variables

    def create_specfile(self):
        """Produce a specfile for a Software Collection metapackage.

        Returns:
            (str) a specfile rendered from a metapackage.spec template
        """
        jinja_env = jinja2.Environment(loader=jinja2.ChoiceLoader([
            jinja2.FileSystemLoader(['/']),
            jinja2.PackageLoader('spec2scl', 'templates'), ]))
        jinja_template = jinja_env.get_template('metapackage.spec')
        return jinja_template.render(data=self)

    def format_variables(self):
        """This function is used to separate given variables into dictionary.

        Returns:
            Dictionary with variables names as keys and values as values
        """
        if self._variables:
            variables = self._variables.split(',')
            return dict([var.split('=') for var in variables])
        return {}

    def format_meta_name(self):
        """This function is used to separate version number from
        meta name of the package.

        Returns:
            Tuple which consists of (meta_name, version)
        """
        r = re.compile('(.*?)([0-9]+)$')
        m = r.match(self._meta_name)
        return (m.group(1).lower(), m.group(2))

    @property
    def meta_name(self):
        try:
            return self.format_meta_name()[0]
        except(AttributeError):
            # If user enters meta package name in wrong format
            # without version number at the end.
            return self._meta_name

    @property
    def meta_version(self):
        try:
            return self.format_meta_name()[1]
        except(AttributeError):
            # If user enters meta package name in wrong format
            # without version number at the end.
            return '2014'

    @property
    def variables(self):
        return self.format_variables()

    @property
    def packager_data(self):
        try:
            packager_name = subprocess.Popen(
                'rpmdev-packager', stdout=subprocess.PIPE).communicate()[0].strip()
        except OSError:
            # Hi John Doe, you should install rpmdevtools
            packager_name = "John Doe <john@doe.com>"
        date_str = time.strftime('%a %b %d %Y', time.gmtime())
        encoding = locale.getpreferredencoding()
        return '{0} {1}'.format(date_str, packager_name.decode(encoding))
