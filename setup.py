# -*- coding: utf-8 -*-
from setuptools import find_packages, setup

with open("README.rst") as readme_file:
    long_description = readme_file.read()

setup(name="keepass_http",
      version="0.4.3",
      description="Python Keepass HTTPD for ChromeIPass and PassIFox",
      long_description=long_description,
      author="Benjamin Hedrich",
      author_email="kiwisauce@pagenotfound.de",
      url="https://github.com/bh/python-keepass-httpd/",
      package_dir={"": "src"},
      packages=find_packages("src/"),
      include_package_data=True,
      install_requires=("colorlog==2.0.0",
                        "daemonize==2.2.3",
                        "docopt==0.6.1",
                        "enum34==0.9.23",
                        "flask==0.10.1",
                        "keepass==1.2",
                        "libkeepass==0.1.2",
                        "lxml==3.2.1"),
      extras_require = {
        'GUI':  ("PySide==1.2.2",)
      },
      entry_points={
          'console_scripts': [
              'python-keepass-httpd = keepass_http.scripts.python_keepass_httpd:main'
          ],
          'keepass_http_backends': [
             'application/x-keepass-database-v1 = keepass_http.backends.python_keepass_backend:Backend',
             'application/x-keepass-database-v2 = keepass_http.backends.libkeepass_backend:Backend'
          ],
      },
      zip_safe=False
)
