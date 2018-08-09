from setuptools import setup

setup(name='modorganizer_umbrella',
      version='2.0',
      description='ModOrganizer 2 Build System',
      url='https://github.com/Modorganizer2/modorganizer-umbrella',
      author='ModOrganizer 2 Team',
      packages=['modorganizer_umbrella'],
      install_requires=[
          'decorator',
          'jinja2',
          'lxml',
          'networkx',
          'patch',
          'psutil',
          'pydot',
          'pydotplus',
          'PyYAML',
          'six'
      ],
      zip_safe=False)