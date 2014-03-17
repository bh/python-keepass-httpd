build_dev_env:
	python setup.py develop
	pip install -r requirements/devel.txt
	
build_test_env:
	python setup.py develop
	pip install -r requirements/testing.txt
	
run_tests:
	py.test --cov=keepass_http --cov-report=term-missing
	
dev_run_tests_verbose:
	py.test --cov=keepass_http --cov-report=term-missing --capture=no
	
dev_test:	dev_build_env	run_tests
	
test:	build_test_env	run_tests
	
show_html_coverage:	dev_test
	rm -rf coverage_html_report/
	coverage html
	xdg-open coverage_html_report/index.html
	
style:
	@echo "Autopep8..."
	autopep8 --aggressive --max-line-length=100 --indent-size=4 \
		 --in-place -r tests/* keepass_http/*
	@echo "Formatting python imports..."
	isort -rc .	
	@echo "Pyflakes..."
	find . -name "*.py" -exec pyflakes {} \;
	
clean:
	-find . -name __pycache__ -type d -exec rm -rf {} \;
	-find . -name "*.pyc" -delete
	-find . -name "*.egg-info" -exec rm -rf {} \;
	-rm -rf dist/ build/
	
publish_release:
	python setup.py sdist --formats=bztar,zip,gztar upload
	python setup.py bdist_wheel upload
