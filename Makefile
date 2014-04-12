PIP=pip
RUN_TESTS=py.test --cov=keepass_http --cov-report=term-missing --cov-report html

build_dev_env:
	$(PIP) install -e .
	$(PIP) install -r requirements/devel.txt
	
build_test_env:
	$(PIP) install -e .
	$(PIP) install -r requirements/testing.txt
	
run_tests:
	$(RUN_TESTS)
	
dev_run_tests_verbose:
	$(RUN_TESTS) --capture=no
	
dev_test: build_dev_env run_tests
	
test: build_test_env run_tests
	
show_html_coverage:	dev_test
	xdg-open coverage_html_report/index.html
	
style:
	@echo "Autopep8..."
	autopep8 --aggressive --max-line-length=100 --indent-size=4 \
		 --in-place -r src/*
	@echo "Formatting python imports..."
	isort -l 100 -rc .	
	@echo "Pyflakes..."
	find . -name "*.py" -exec pyflakes {} \;
	
clean:
	-find . -name __pycache__ -type d | xargs rm -rf
	-find . -name "*.pyc"| xargs rm -f
	-rm -rf dist/ build/ src/*.egg-info
	
bumpversion:
	bumpversion part --new-version $(VERSION)
	
publish_release:
	python setup.py sdist --formats=bztar,zip,gztar upload
	python setup.py bdist_wheel upload
