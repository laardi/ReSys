#Modified by Sampsa

import unittest, copy
import json

import flask

import resys.resources as resources
import resys.database

db_path ='db/test.db'
db = resys.database.ResysDatabase(db_path)
initial_messages = 20
initial_users = 5
resources.app.config['TESTING'] = True
resources.app.config['DATABASE'] = db
class ResourcesAPITestCase(unittest.TestCase):
   
    def setUp(self):
        db.load_init_values()
        self.client = resources.app.test_client()

    def tearDown(self):
        db.clean()


class UsersTestCase (ResourcesAPITestCase):
   
    url = '/resys/api/users/'
    
    user = "sampus"
    user_profile = {"template":{"data":[
                    {"prompt": "Insert useraccount",
                     "name":"useraccount",
                     "value": "sampus"},
                    {"prompt": "Insert email",
                     "name":"email",
                     "value": "kivet@pussis.sa"},
                    {"prompt": "Insert firstname",
                     "name":"firstname",
                     "value": "esa"},
                    {"prompt": "Insert lastname",
                     "name":"lastname",
                     "value": "nahka"}
                    ]}}
    user_profile2 = {"template":{"data":[
                    {"prompt": "Insert useraccount",
                     "name":"useraccount",
                     "value": "sampooko"},
                    {"prompt": "Insert email",
                     "name":"email",
                     "value": "kivet@pssussis.sa"},
                    {"prompt": "Insert firstname",
                     "name":"firstname",
                     "value": "essa"},
                    {"prompt": "Insert lastname",
                     "name":"lastname",
                     "value": "nahhka"}
                    ]}}


    @classmethod
    def setUpClass(cls):
        print 'Testing UsersTestCase'
    
    def test_url(self):
        '''
        Checks that the URL points to the right resource
        '''
        #NOTE: self.shortDescription() shuould work.
        print '('+self.test_url.__name__+')', self.test_url.__doc__, 
        with resources.app.test_request_context(self.url):
            rule = flask.request.url_rule
            view_point = resources.app.view_functions[rule.endpoint].view_class
            self.assertEquals(view_point, resources.Users)
    
    def test_get_users(self):
        '''
        Checks that GET users return correct status code and data format
        '''
        print '('+self.test_get_users.__name__+')', self.test_get_users.__doc__
        #I use this because I need the app context to use the api.url_for
        with resources.app.test_client() as client:
            resp = client.get(self.url)
            self.assertEquals(resp.status_code,200)
            data = json.loads(resp.data)
            user0 = data['collection']["items"][0]
            self.assertEquals(user0['data'][0]['name'],'useraccount')
            self.assertEquals(user0['read-only'], True)
            self.assertEquals(user0['href'],resources.api.url_for(resources.User, useraccount=user0['data'][0]['value']))
            

    def test_add_user(self):
        '''
        Checks that the user is added correctly

        '''
        print '('+self.test_add_user.__name__+')', self.test_add_user.__doc__
        resp = self.client.post(self.url,
                                data=json.dumps(self.user_profile),
                                headers={"Content-Type":"application/json"})
        self.assertEquals(resp.status_code, 201)
        self.assertIn('Location', resp.headers)
        resp2 = self.client.get(self.url)
        self.assertEquals(resp2.status_code, 200)    

    
    def test_add_user_missing_mandatory(self):
        '''
        Test that it returns error when is missing a mandatory data 
        '''
        print '('+self.test_add_user_missing_mandatory.__name__+')', self.test_add_user_missing_mandatory.__doc__
        mandatory = ['firstname', 'lastname', 'email', 'useraccount']
        #Iterate through all the attributes from the list, remove one of them in 
        #each iteration. Be sure that always return status code 400
        i = 0
        for attribute in mandatory:
            user = copy.deepcopy(self.user_profile)
            del user["template"]["data"][i]
            resp = self.client.post(self.url,
                                    data=json.dumps(user),
                                    headers={"Content-Type":"application/json"})
            self.assertEquals(resp.status_code, 400)
            i = i+1

    def test_add_existing_user(self):
        '''
        Testign that trying to add an existing user will fail

        '''
        print '('+self.test_add_existing_user.__name__+')', self.test_add_existing_user.__doc__
        resp = self.client.post(self.url,
                                data=json.dumps(self.user_profile2),
                                headers={"Content-Type":"application/json"})
        self.assertEquals(resp.status_code, 409)

class UserTestCase (ResourcesAPITestCase):
    user1 = 'sampooko'
    user2 = 'kaarle'
    user3 = 'kille'
    url1 = '/resys/api/users/%s/'% user1
    url2 = '/resys/api/users/%s/'% user2
    url3 = '/resys/api/users/%s/'% user3
    url_wrong = '/resys/api/users/unknown/'

    {"template":{
        "data":[
            {"prompt":"","name":"firstname","value":"Aziz"},
            {"prompt":"","name":"lastname","value":"Habeb"},
            {"prompt":"","name":"mobile","value":"46999888"},
            {"prompt":"","name":"email","value":"asd@fgh.kl"}
            ]
        }
    }



    user_modified = {"template":{
                        "data":[
                            {"prompt":"","name":"firstname","value":"Aziz"},
                            {"prompt":"","name":"lastname","value":"Habeb"},
                            {"prompt":"","name":"mobile","value":"46999888"},
                            {"prompt":"","name":"email","value":"asd@fgh.kl"}
                            ]
                        }
                    }

    user_modified_wrong = {"template":{"data":{
					u"firstname":u"Peter", 
					u"email":u"hampookon@perse.de",
                    u"mobile":"050000000"}}}

    @classmethod
    def setUpClass(cls):
        print 'Testing UserTestCase'

    def setUp(self):
        super(UserTestCase,self).setUp()
        #Copy the user in here since later we are going to modify it
        self.user = {u"useraccount":u"sampooko",					
					u"firstname":u"Peter", 
					u"lastname":u"DonNadie",
					u"email":u"hampookon@perse.de"}

    def test_url(self):
        '''
        Checks that the URL points to the right resource
        '''
        #NOTE: self.shortDescription() shuould work.
        print '('+self.test_url.__name__+')', self.test_url.__doc__
        with resources.app.test_request_context(self.url1):
            rule = flask.request.url_rule
            view_point = resources.app.view_functions[rule.endpoint].view_class
            self.assertEquals(view_point, resources.User)
    
    def test_get_format(self):
        '''
        Checks that the format of user is correct

        '''
        print '('+self.test_get_format.__name__+')', self.test_get_format.__doc__
        resp = self.client.get(self.url1)
        data = json.loads(resp.data)
        self.assertEquals(resp.status_code, 200)
        self.assertIn('_links', data)
        self.assertIn('firstname', data)
        self.assertIn('lastname', data)
        self.assertIn('email', data)
        self.assertIn('mobile', data)
        self.assertIn('useraccount', data)
        self.assertIn('template', data)
        for attribute in ('reservations', 'self', 'collection'):
            self.assertIn(attribute, data['_links'])

    def test_get_wrong_id(self):
        '''
        check for correct response with wrong id
        '''

        print '('+self.test_get_wrong_id.__name__+')', self.test_get_wrong_id.__doc__
        resp = self.client.get(self.url_wrong)
        self.assertEquals(resp.status_code, 404)

    def test_modify_user(self):
        '''
        test for correct status code and format
        '''
        print '('+self.test_modify_user.__name__+')', self.test_modify_user.__doc__
        resp = self.client.put(self.url1, 
                data=json.dumps(self.user_modified), 
                headers={'Accept':'application/json','Content-Type':'application/vnd.collection-json'})
        self.assertEquals(resp.status_code, 204)
        #Check that the message has been modified
        resp2 = self.client.get(self.url1)
        self.assertEquals(resp2.status_code, 200)
        data = json.loads(resp2.data)
        #Check that the title and the body of the message has been modified with the new data
        self.assertEquals("Aziz", data["firstname"])
        self.assertEquals("Habeb", data["lastname"])
        #self.assertEquals(data['message']['title'],message_1_request)

    def test_modify_unexisting_user(self):
        '''
        Try to modify a user that does not exist
        '''
        print '('+self.test_modify_unexisting_user.__name__+')', self.test_modify_unexisting_user.__doc__
        resp = self.client.put(self.url_wrong,
                                data=json.dumps(self.user_modified),
                                headers={"Content-Type":"application/json"})
        self.assertEquals(resp.status_code, 404)

    def test_modify_wrong_data(self):
        '''
        Try to modify a user sending wrong data
        '''
        print '('+self.test_modify_wrong_data.__name__+')', self.test_modify_wrong_data.__doc__
        resp = self.client.put(self.url1,
                                data=json.dumps(self.user_modified_wrong),
                                headers={"Content-Type":"application/json"})
        self.assertEquals(resp.status_code, 400)

    def test_delete_user(self):
        '''
        Checks that Delete user return correct status code if deleted correctly
        '''
        print '('+self.test_delete_user.__name__+')', self.test_delete_user.__doc__
        resp = self.client.delete(self.url2)
        self.assertEquals(resp.status_code, 204)
        resp2 = self.client.get(self.url2)
        self.assertEquals(resp2.status_code, 404)

    def test_delete_unexisting_user(self):
        '''
        Checks that Delete user return correct status code if given a wrong address
        '''
        print '('+self.test_delete_unexisting_user.__name__+')', self.test_delete_unexisting_user.__doc__
        resp = self.client.delete(self.url_wrong)
        self.assertEquals(resp.status_code, 404)


if __name__ == '__main__':
    print 'Start running tests'
    unittest.main()
