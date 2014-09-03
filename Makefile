.PHONY: sandbox

USER=admin
EMAIL=admin@tangentsnowball.com.au

postgres-db:
	- psql -U postgres -h localhost -c 'drop database devdb;'
	psql -U postgres -h localhost -c 'create database devdb;'

sandbox:
	python sandbox/manage.py syncdb --noinput
	python sandbox/manage.py migrate
	python sandbox/manage.py oscar_import_catalogue sandbox/data/books-catalogue.csv
	python sandbox/manage.py loaddata countries.json
	echo "Creating superuser '$(USER)' with email '$(EMAIL)'"
	python sandbox/manage.py createsuperuser --username=$(USER) --email=$(EMAIL)

pypi-release:
	rm -rf dist/*
	python setup.py sdist bdist_wheel
	twine upload dist/* -r pypi-snowball
