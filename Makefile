.PHONY: sandbox

USER=admin
EMAIL=admin@tangentsnowball.com.au

sandbox:
	python sandbox/manage.py syncdb --noinput
	python sandbox/manage.py migrate
	python sandbox/manage.py oscar_import_catalogue sandbox/data/books-catalogue.csv
	python sandbox/manage.py loaddata countries.json
	echo "Creating superuser '$(USER)' with email '$(EMAIL)'"
	python sandbox/manage.py createsuperuser --username=$(USER) --email=$(EMAIL)
