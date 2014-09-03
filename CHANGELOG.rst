=========
Changelog
=========

0.1.1
-----

* Add tests for migrations using PostgreSQL and MySQL databases on Travis
* Add a fix for MySQL when renaming tables in migration ``0004`` which fails
  if constraints on the foreign keys are not dropped before renaming them. This is
  details in ticket #466 for South: http://south.aeracode.org/ticket/466
* Fix dependency with Oscar's ``basket`` app in eway migration.
* Rename deprecated tables in migration due to PostgreSQL issue with uppercase
  names.


0.1.0
-----

* Initial version of the project.
