ReSys is a reservation system created for a programmable web course. ReSys is a RESTful web service that offers an opportunity to create a simple reservation service.

How to start the server:

	 -run "python -m resys.resources" in console

How to start the text-based client:
	 
	 -run "python client.py"
	 
Running tests:
	Tests are run from the operating folder.
	 - To run all the tests, type "python run_all_tests.py"
	 - To run a single test, type "python -m test.<NAME-OF-THE-TEST-FILE>"

Testfiles:

	 * API:
	   - resys_api_tests_items
	   - resys_api_tests_users
	   - resys_api_tests_reservations
	 * DATABASE
	   - resys_database_api_tests_items
	   - resys_database_api_tests_reservations
	   - resys_database_api_tests_user
