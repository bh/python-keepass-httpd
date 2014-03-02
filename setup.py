import sys

from setuptools import setup, find_packages

with open("requirements/package.txt") as requirements_file:
    requirements = requirements_file.read().splitlines()

setup(name="keepass_http",
      version="0.2",
      description="Python Keepass HTTPD for ChromeIPass",
      author="Benjamin Hedrich",
      author_email="kiwisauce@pagenotfound.de",
      url="https://github.com/bhedrich/python-keepass-httpd/",
      package_dir = {"": "src"},
      packages = find_packages("src/", exclude="tests"),
      install_requires=requirements,
      entry_points={"console_scripts":
                        ["python-keepass-httpd = python_keepass_httpd:main"]
      },
      zip_safe=False,
      #data_files=[('usr/share/config', ['bla.conf']),],
)
