.PHONY: sandbox

USER=admin
EMAIL=admin@tangentsnowball.com.au

sandbox:
	sandbox/manage.py syncdb --noinput
	sandbox/manage.py migrate
	sandbox/manage.py oscar_import_catalogue sandbox/data/books-catalogue.csv
	sandbox/manage.py loaddata countries.json
	echo "Creating superuser '$(USER)' with email '$(EMAIL)'"
	sandbox/manage.py createsuperuser --username=$(USER) --email=$(EMAIL)
