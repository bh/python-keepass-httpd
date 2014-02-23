
from setuptools import setup


setup(name='keepass_http',
      version='0.2',
      description='Python Keepass HTTPD for ChromeIPass',
      author='Benjamin Hedrich',
      author_email='kiwisauce@pagenotfound.de',
      url='https://github.com/bhedrich/python-keepass-httpd/',
      zip_safe=False,
      packages=["keepass_http"],
      scripts=["scripts/python-keepass-httpd.py"],
      install_requires=open("requirements/package.txt").read().splitlines(),
)
