from setuptools import find_packages, setup

with open("requirements/package.txt") as requirements_file:
    requirements = requirements_file.read().splitlines()

setup(name="keepass_http",
      version="0.3",
      description="Python Keepass HTTPD for ChromeIPass",
      author="Benjamin Hedrich",
      author_email="kiwisauce@pagenotfound.de",
      url="https://github.com/bhedrich/python-keepass-httpd/",
      package_dir={"": "src"},
      packages=find_packages("src/", exclude="tests"),
      install_requires=requirements,
      scripts=["bin/python_keepass_httpd"],
      include_package_data=True,
      data_files=[("conf", ["conf/logging.conf"])],
      zip_safe=False,
)
