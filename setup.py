# Copyright 2013 Simon Dominic Hibbs
from distutils.core import setup
import py2exe

# The following option is the prevent including W7 specific libraries
# when building on W7.
# dll_excludes=[ 'mswsock.dll', 'powrprof.dll' ]
#
# User machines may need MSVCP90.dll:
# http://www.microsoft.com/en-us/download/details.aspx?id=29


setup(name='StarBase',
      version='0.24',
      author='Simon D. Hibbs',
      windows=[{'script' : 'Starbase.pyw'}],
      options={'py2exe' : {'bundle_files' : '1',
                           "dll_excludes": ["MSVCP90.dll"]}},
      scripts=['log.py'],
      dll_excludes=[ 'mswsock.dll', 'powrprof.dll' ],
      data_files=[('', ['projects.ini',
                        'WorldNames.txt']),
                  ('rules_templates', ['rules_templates\\Info.txt',]),
                  ('rules_templates\\2D6_OGL', ['rules_templates\\2D6_OGL\\OGL_License.txt',
                                                'rules_templates\\2D6_OGL\\Rules.py',
                                                'rules_templates\\2D6_OGL\\D6_OGL.py',
                                                'rules_templates\\2D6_OGL\\RulesInfo.txt']),
                  ('rules_templates\\default', ['rules_templates\\default\\Rules.py',
                                                'rules_templates\\default\\RulesInfo.txt'])]
      )
