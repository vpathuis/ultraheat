from setuptools import setup

# read the contents of your README file
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="ultraheat_api",
    version="0.5.5",
    description="Reading usage data from the Landys & Gyr Ultraheat heat meter unit",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/vpathuis/ultraheat",
    author="vpathuis",
    license="MIT",
    packages=["ultraheat_api"],
    install_requires=[
        "pyserial",
    ],
    zip_safe=False,
)
