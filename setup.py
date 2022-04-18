from setuptools import setup

# read the contents of your README file
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(name='uh50_api',
      version='0.2.4',
      description='Reading usage data from the Landys & Gyr UH50 heat measuring unit',
      long_description=long_description,
      long_description_content_type='text/markdown',
      url='https://github.com/vpathuis/uh50',
      author='vpathuis',
      license='MIT',
      packages=['uh50_api'],
      install_requires=[
          'pyserial',
      ],
      zip_safe=False)
