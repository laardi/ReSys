import os

api_users = os.system('python -m test.resys_api_tests_users')

api_items =  os.system('python -m test.resys_api_tests_items')

api_reservations =  os.system('python -m test.resys_api_tests_reservations')

db_users = os.system('python -m test.resys_api_tests_users')

db_items = os.system('python -m test.resys_api_tests_users')

db_reservations = os.system('python -m test.resys_api_tests_users')
