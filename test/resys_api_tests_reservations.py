

import unittest, copy
import json

import flask

import resys.resources as resources
import resys.database

db_path ='db/tessdt.db'
db = resys.database.ResysDatabase(db_path)
initial_reservations = 2
initial_users = 5
resources.app.config['TESTING'] = True
resources.app.config['DATABASE'] = db
class ResourcesAPITestCase(unittest.TestCase):
   
    def setUp(self):
        db.load_init_values()
        self.client = resources.app.test_client()

    def tearDown(self):
        db.clean()

class ReservationsTestCase (ResourcesAPITestCase):
    url = '/resys/api/reservations/'
    new_reservation = {"template":{"data":[
            {"prompt" : "Insert useraccount", "name" : "user",
             "value" : "kaarle"},
            {"prompt" : "Insert item ID", "name" : "item",
             "value" : "1"},
            {"prompt" : "Insert time of loan", "name" : "ldate",
             "value" : "1435660760"},
            {"prompt" : "Insert time of return", "name" : "rdate",
             "value" : None}
             ]}}

    new_reservation_wrong_user = {"template":{"data":[
            {"prompt" : "Insert useraccount", "name" : "user",
             "value" : "nobody"},
            {"prompt" : "Insert item ID", "name" : "item",
             "value" : "1"},
            {"prompt" : "Insert time of loan", "name" : "ldate",
             "value" : "123123123"},
            {"prompt" : "Insert time of return", "name" : "rdate",
             "value" : None}
             ]}}

    new_reservation_wrong_item= {"template":{"data":[
            {"prompt" : "Insert useraccount", "name" : "user",
             "value" : "hampooko"},
            {"prompt" : "Insert item ID", "name" : "item",
             "value" : "12"},
            {"prompt" : "Insert time of loan", "name" : "ldate",
             "value" : "1435660760"},
            {"prompt" : "Insert time of return", "name" : "rdate",
             "value" : None}
                        ]}}
    new_reservation_wrong_format = {"template":{"data":[
            {"prompt" : "Insert useraccount", "name" : "user",
             "value" : "hampooko"},
            {"prompt" : "Insert item ID", "name" : "item",
             "value" : "1"},
            {"prompt" : "Insert time of loan", "name" : "ldate",
             "value" : None},
            {"prompt" : "Insert time of return", "name" : "rdate",
             "value" : None}
                            ]}}
    new_reservation_response = {
       "ldate": 1435660760,
       "item": 1,
       "rdate": None,
       "_links": {
            "items": {
            "profile": "link to item profile",
                "href": "/resys/api/items/",
                "type": "application/vnd.collection+json"
               },
            "self": {
                "profile": "link to reservation profile",
                "href": "/resys/api/reservations/2/",
                "type": "application/hal+json"
                },
            "users": {
               "profile": "link to user profile",
               "href": "/resys/api/users/",
            "type": "application/vnd.collection+json"
               },
            "collection": {
               "profile": "link to reservation profile",
               "href": "/resys/api/reservations/",
               "type": "application/vnd.collection+json"
               }
            },
       "user": "kaarle",
       "template": {
            "data": [{
                "required": True,
                "prompt": "Insert useraccount",
                "name": "user",
                "value": ""
                },
                {
                "required": True,
                "prompt": "Insert item id",
                "name": "item",
                "value": ""
                },
                {
                "required": True,
                "prompt": "Insert loan date",
                "name": "ldate",
                "value": ""
                },
                {
                "required": False,
                "prompt": "insert return date",
                "name": "rdate",
                "value": ""
                }
                ]
            },
        "reservation_ID": 3
         }

        
    #@classmethod
    def setUpClass(cls):
        print 'Testing ReservationsTestCase'
    
    def test_url(self):
        '''
        Checks that the URL points to the right resource
        '''
        #NOTE: self.shortDescription() shuould work.
        print '('+self.test_url.__name__+')', self.test_url.__doc__, 
        with resources.app.test_request_context(self.url):
            rule = flask.request.url_rule
            view_point = resources.app.view_functions[rule.endpoint].view_class
            self.assertEquals(view_point, resources.Reservations)
    
    def test_get_reservations(self):
        '''
        Checks that GET Reservations returns correct status code and data format
        '''
        print '('+self.test_get_reservations.__name__+')', self.test_get_reservations.__doc__
        #I use this because I need the app context to use the api.url_for
        with resources.app.test_client() as client:
            resp = client.get(self.url)
            self.assertEquals(resp.status_code,200)
            data = json.loads(resp.data)
            #link = data['links']
            #self.assertEquals(link[0]['title'],'item')
            #self.assertEquals(link[0]['rel'],'self')
            #self.assertEquals(link[0]['href'],resources.api.url_for(resources.Users))
            reservations = data["collection"]["items"]
            self.assertEquals(len(reservations),initial_reservations)
            #Just check one message the rest are constructed in the same way
            reservation0 =reservations [0]
            self.assertIn('data',reservation0)
            self.assertIn('href',reservation0)
            self.assertIn('read-only',reservation0)
            #The link contains a url to a message

    def test_post_reservation(self):
        '''
        Checks that POST reservation returns correct status code when file format is ok
        '''
        print '('+self.test_post_reservation.__name__+')', self.test_post_reservation.__doc__

        resp = self.client.post(self.url,data=json.dumps(self.new_reservation),
                                headers={"Accept":"application/json","Content-Type":"application/json"})
        self.assertEquals(resp.status_code, 201)
        self.assertIn('Location', resp.headers)
        reservation_url = resp.headers['Location']

        #Check that the reservation stored
        resp2 = self.client.get(reservation_url)
        self.assertEquals(resp2.status_code, 200)
        data = json.loads(resp2.data)
        self.assertEquals(self.new_reservation_response['user'], data['user'])
        self.assertEquals(self.new_reservation_response['item'], data['item'])
        self.assertEquals(self.new_reservation_response['ldate'], data['ldate'])
        self.assertEquals(self.new_reservation_response['reservation_ID'], data['reservation_ID'])


    def test_post_reservation_wrong_format(self):
        '''
        Tries to add a new reservation with wrong format
        '''

        print '('+self.test_post_reservation_wrong_format.__name__+')', self.test_post_reservation_wrong_format.__doc__

        resp = self.client.post(self.url,data=json.dumps(self.new_reservation_wrong_format),
                                headers={"Accept":"application/json","Content-Type":"application/json"})
        self.assertEquals(resp.status_code, 400)
    
    def test_post_reservation_wrong_user(self):
        '''
        Tries to add a new reservation with wrong user id and item id
        '''

        print '('+self.test_post_reservation_wrong_user.__name__+')', self.test_post_reservation_wrong_user.__doc__

        resp = self.client.post(self.url,data=json.dumps(self.new_reservation_wrong_user),
                                headers={"Accept":"application/json","Content-Type":"application/json"})
        self.assertEquals(resp.status_code, 409)
    def test_post_reservation_wrong_item(self):
        '''
        Tries to add a new reservation with wrong item id
        '''

        print '('+self.test_post_reservation_wrong_item.__name__+')', self.test_post_reservation_wrong_item.__doc__

        resp = self.client.post(self.url,data=json.dumps(self.new_reservation_wrong_user),
                                headers={"Accept":"application/json","Content-Type":"application/json"})
        self.assertEquals(resp.status_code, 409)


class ReservationTestCase (ResourcesAPITestCase):
    
    #ATTENTION: json.loads return unicode
    url = '/resys/api/reservations/1/'
    url_wrong = '/resys/api/reservations/23/'
    reservation_request_modified = {"template":{"data":{
                        "item":1,
                        "user":"kaarle",
                        "ldate":1435660760,
                        "rdate":None
                        }}}
    reservation_request_modified_response = {"template":{"data":{
                        "item":u"Hampooko cave",
                        "user":u"kaarle",
                        "ldate":1435660760,
                        "rdate":None
                        }}}
    reservation_request_modified_wrong = {
                        "item":1,
                        "user":"kille",
                        "rdate":None
                    }

 
    @classmethod
    def setUpClass(cls):
        print 'Testing ReservationTestCase'
    
    
    def test_url(self):
        '''
        Checks that the URL points to the right resource
        '''
        #NOTE: self.shortDescription() shuould work.
        print '('+self.test_url.__name__+')', self.test_url.__doc__
        with resources.app.test_request_context(self.url):
            rule = flask.request.url_rule
            view_point = resources.app.view_functions[rule.endpoint].view_class
            self.assertEquals(view_point, resources.Reservation)
    
    def test_wrong_url(self):
        '''
        Checks that GET reservation returns correct status code if given a wrong reservation id
        '''
        print '('+self.test_wrong_url.__name__+')', self.test_wrong_url.__doc__
        resp = self.client.get(self.url_wrong)
        self.assertEquals(resp.status_code, 404)


    def test_get_reservation(self):
        '''
        Checks that GET reservation returns correct status code and data format
        '''
        print '('+self.test_get_reservation.__name__+')', self.test_get_reservation.__doc__
        with resources.app.test_client() as client:
            resp = client.get(self.url)
            self.assertEquals(resp.status_code ,200)
            data = json.loads(resp.data)
            #The data is formed by links and reservation
            links = data['links']
            reservation = data ['reservation']

            #Check that the link format is correct
            self.assertEquals(len(links), 1)
            link0 = links[0]
            self.assertEquals(link0['title'],'reservations')
            self.assertEquals(link0['rel'],'collection')
            self.assertEquals(link0['href'], resources.api.url_for(resources.Reservations))
            
            #Check that the reservation contains all required attributes
            for attribute in ('id', 'user', 'item', 'ldate','rdate'):
                self.assertIn(attribute, reservation)

    def test_modify_reservation(self):
        '''
        Modify an existing reservation and check that the reservation has been modified correctly in the server
        '''
        print '('+self.test_modify_reservation.__name__+')', self.test_modify_reservation.__doc__
        resp = self.client.put(self.url, 
                data=json.dumps(self.reservation_request_modified), 
                headers={'Accept':'application/json','Content-Type':'application/json'})
        self.assertEquals(resp.status_code, 204)
        #Check that the message has been modified
        resp2 = self.client.get(self.url)
        self.assertEquals(resp2.status_code, 200)
        data = json.loads(resp2.data)
        #Check that the title and the body of the message has been modified with the new data
        self.assertDictContainsSubset(self.reservation_request_modified_response, data['reservation'])
        #self.assertEquals(data['message']['title'],message_1_request)

    def test_modify_unexisting_reservation(self):
        '''
        Try to modify an reservation that does not exist
        '''
        print '('+self.test_modify_unexisting_reservation.__name__+')', self.test_modify_unexisting_reservation.__doc__
        resp = self.client.put(self.url_wrong,
                                data=json.dumps(self.reservation_request_modified),
                                headers={"Content-Type":"application/json"})
        self.assertEquals(resp.status_code, 404)

    def test_modify_wrong_reservation(self):
        '''
        Try to modify a reservation sending wrong data
        '''
        print '('+self.test_modify_wrong_reservation.__name__+')', self.test_modify_wrong_reservation.__doc__
        resp = self.client.put(self.url,
                                data=json.dumps(self.reservation_request_modified_wrong),
                                headers={"Content-Type":"application/json"})
        self.assertEquals(resp.status_code, 400)

    def test_delete_reservation(self):
        '''
        Checks that Delete reservation return correct status code if deleted correctly
        '''
        print '('+self.test_delete_reservation.__name__+')', self.test_delete_reservation.__doc__
        resp = self.client.delete(self.url)
        self.assertEquals(resp.status_code, 204)
        resp2 = self.client.get(self.url)
        self.assertEquals(resp2.status_code, 404)

    def test_delete_unexisting_reservation(self):
        '''
        Checks that Delete reservation return correct status code if given a wrong address
        '''
        print '('+self.test_delete_unexisting_reservation.__name__+')', self.test_delete_unexisting_reservation.__doc__
        resp = self.client.delete(self.url_wrong)
        self.assertEquals(resp.status_code, 404)


class UserReservationsTestCase (ResourcesAPITestCase):
    initial_reservs = 1
    user1 = "sampooko"
    user2 = "nobody"
    url = '/resys/api/users/%s/userreservations/' %user1
    wrong_url = '/resys/api/users/%s/userreservations/' %user2
    

   
    #@classmethod
    def setUpClass(cls):
        print 'Testing ReservationsTestCase'
    
    def test_url(self):
        '''
        Checks that the URL points to the right resource
        '''
        #NOTE: self.shortDescription() shuould work.
        print '('+self.test_url.__name__+')', self.test_url.__doc__, 
        with resources.app.test_request_context(self.url):
            rule = flask.request.url_rule
            view_point = resources.app.view_functions[rule.endpoint].view_class
            self.assertEquals(view_point, resources.UserReservations)
    
    def test_get_reservations(self):
        '''
        Checks that GET Reservations returns correct status code and data format
        '''
        print '('+self.test_get_reservations.__name__+')', self.test_get_reservations.__doc__
        #I use this because I need the app context to use the api.url_for
        with resources.app.test_client() as client:
            resp = client.get(self.url)
            self.assertEquals(resp.status_code,200)
            data = json.loads(resp.data)
            
            reservations = data['reservations']
            self.assertEquals(len(reservations),self.initial_reservs)
            #Just check one message the rest are constructed in the same way
            reservation0 =reservations [0]
            self.assertIn('id',reservation0)
            self.assertIn('item',reservation0)
            self.assertIn('user',reservation0)
            self.assertIn('loandate',reservation0)
            self.assertIn('returndate',reservation0)
            self.assertIn('link',reservation0)
            link0 = reservation0['link']
            #The link contains a url to a message
            self.assertIn(resources.api.url_for(resources.Reservations),link0['href'])

    def test_get_reservations_invalid_user(self):
        '''
        Checks that GET Reservations returns correct status code and data format
        '''
        print '('+self.test_get_reservations_invalid_user.__name__+')', self.test_get_reservations_invalid_user.__doc__
        #I use this because I need the app context to use the api.url_for
        with resources.app.test_client() as client:
            resp = client.get(self.wrong_url)
            self.assertEquals(resp.status_code,404)
            
class ItemReservationsTestCase (ResourcesAPITestCase):
    initial_reservs = 1
    item1 = 1
    item2 = 52
    url = '/resys/api/items/%s/itemreservations/' %item1
    wrong_url = '/resys/api/items/%s/itemreservations/' %item2
    

   
    #@classmethod
    def setUpClass(cls):
        print 'Testing ReservationsTestCase'
    
    def test_url(self):
        '''
        Checks that the URL points to the right resource
        '''
        #NOTE: self.shortDescription() shuould work.
        print '('+self.test_url.__name__+')', self.test_url.__doc__, 
        with resources.app.test_request_context(self.url):
            rule = flask.request.url_rule
            view_point = resources.app.view_functions[rule.endpoint].view_class
            self.assertEquals(view_point, resources.ItemReservations)
    
    def test_get_reservations(self):
        '''
        Checks that GET itemReservations returns correct status code and data format
        '''
        print '('+self.test_get_reservations.__name__+')', self.test_get_reservations.__doc__
        #I use this because I need the app context to use the api.url_for
        with resources.app.test_client() as client:
            resp = client.get(self.url)
            self.assertEquals(resp.status_code,200)
            data = json.loads(resp.data)
            
            reservations = data['reservations']
            self.assertEquals(len(reservations),self.initial_reservs)
            #Just check one message the rest are constructed in the same way
            reservation0 =reservations [0]
            self.assertIn('id',reservation0)
            self.assertIn('item',reservation0)
            self.assertIn('user',reservation0)
            self.assertIn('loandate',reservation0)
            self.assertIn('returndate',reservation0)
            self.assertIn('link',reservation0)
            link0 = reservation0['link']
            #The link contains a url to a message
            self.assertIn(resources.api.url_for(resources.Reservations),link0['href'])

    def test_get_reservations_invalid_item(self):
        '''
        Checks that get with wrong item returns 404
        '''
        print '('+self.test_get_reservations_invalid_item.__name__+')', self.test_get_reservations_invalid_item.__doc__
        #I use this because I need the app context to use the api.url_for
        with resources.app.test_client() as client:
            resp = client.get(self.wrong_url)
            self.assertEquals(resp.status_code,404)

if __name__ == '__main__':
    print 'Start running tests'
    unittest.main()
