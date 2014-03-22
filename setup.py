from setuptools import find_packages, setup

with open("README.rst") as readme_file:
    long_description = readme_file.read()

setup(name="keepass_http",
      version="0.3.6",
      description="Python Keepass HTTPD for ChromeIPass",
      long_description=long_description,
      author="Benjamin Hedrich",
      author_email="kiwisauce@pagenotfound.de",
      url="https://github.com/bhedrich/python-keepass-httpd/",
      package_dir={"": "src"},
      packages=find_packages("src/"),
      include_package_data=True,
      install_requires=("pycrypto==2.6.1",
                        "keepass==1.1",
                        "wsgiref==0.1.2",
                        "python-daemon==1.6",
                        "docopt==0.6.1",
                        "setproctitle==1.1.8",
                        "libkeepass==0.1.2",
                        "lxml==3.2.1"),
      entry_points={
          'console_scripts': [
              'python-keepass-httpd = keepass_http.scripts.python_keepass_httpd:main'
          ],
          'keepass_http_backends': [
             'application/x-keepass-database-v1 = keepass_http.backends.python_keepass_backend:Backend',
          ],
    },
    zip_safe=False
)
