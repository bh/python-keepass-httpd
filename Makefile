default:
	all
	
all:
	test
	
build_env:
	python setup.py develop > /dev/null
	pip install -r requirements/testing.txt > /dev/null
	
test_debug:	build_env
	py.test --cov=keepass_http --cov-report=term-missing --capture=no
	
test:	build_env
	run_tests
	
run_tests:
	py.test --cov=keepass_http --cov-report=term-missing
	
show_html_coverage:	test
	rm -rf coverage_html_report/
	coverage html
	xdg-open coverage_html_report/index.html
	
style:
	@echo "Autopep8..."
	autopep8 --aggressive --max-line-length=100 --indent-size=4 \
		 --in-place -r setup.py scripts/* tests/* keepass_http/*
	@echo "Formatting python imports..."
	isort -rc .	
	@echo "Pyflakes..."
	find . -name "*.py" -exec pyflakes {} \;
