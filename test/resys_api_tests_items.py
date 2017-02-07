

import unittest, copy
import json

import flask

import resys.resources as resources
import resys.database

db_path ='db/test.db'
db = resys.database.ResysDatabase(db_path)
initial_items = 3
initial_users = 5
resources.app.config['TESTING'] = True
resources.app.config['DATABASE'] = db
class ResourcesAPITestCase(unittest.TestCase):
   
    def setUp(self):
        db.load_init_values()
        self.client = resources.app.test_client()

    def tearDown(self):
        db.clean()

class ItemsTestCase (ResourcesAPITestCase):

    url = '/resys/api/items/'
    new_item = {"template":{
          "data" : [
            {"prompt" : "", "name" : "name", "value" : "Classroom of Despair"},
            {"prompt" : "", "name" : "description", "value" : "A room where all hope is lost and meaning of life disappears"},
            {"prompt" : "", "name" : "status", "value" : "0"}
                ]
            }}
    new_item_wrong_format ={"template":{
          "data" : [
            {"prompt" : "", "name" : "name", "value" : "Classroom of Despair"},
            {"prompt" : "", "name" : "description", "value" : "A room where all hope is lost and meaning of life disappears"}
                ]
            }}
    new_item_response = {
        u"name":u"Classroom of Despair",
        u"description":u"A room where all hope is lost and meaning of life disappears",
        u"status":0
        }
   
    @classmethod
    def setUpClass(cls):
        print 'Testing ItemsTestCase'
    
    def test_url(self):
        '''
        Checks that the URL points to the right resource
        '''
        #NOTE: self.shortDescription() shuould work.
        print '('+self.test_url.__name__+')', self.test_url.__doc__, 
        with resources.app.test_request_context(self.url):
            rule = flask.request.url_rule
            view_point = resources.app.view_functions[rule.endpoint].view_class
            self.assertEquals(view_point, resources.Items)
    
    def test_get_items(self):
        '''
        Checks that GET Items returns correct status code and data format
        '''
        print '('+self.test_get_items.__name__+')', self.test_get_items.__doc__
        #I use this because I need the app context to use the api.url_for
        with resources.app.test_client() as client:
            resp = client.get(self.url)
            self.assertEquals(resp.status_code,200)
            data = json.loads(resp.data)
            
            items = data['collection']['items']
            self.assertEquals(len(items),initial_items)
            #Just check one message the rest are constructed in the same way
            item0 =items [0]
            self.assertIn('href',item0)
            self.assertIn('read-only',item0)
            self.assertIn('data',item0)

    def test_post_item(self):
        '''
        Checks that POST Item returns correct status code when file format is ok
        '''
        print '('+self.test_post_item.__name__+')', self.test_post_item.__doc__

        resp = self.client.post(self.url,data=json.dumps(self.new_item),
                                headers={"Accept":"application/json","Content-Type":"application/json"})
        self.assertEquals(resp.status_code, 201)
        self.assertIn('Location', resp.headers)
        item_url = resp.headers['Location']

        #Check that the item stored
        resp2 = self.client.get(item_url)
        self.assertEquals(resp2.status_code, 200)
        data = json.loads(resp2.data)
        self.assertEqual(self.new_item_response['name'],data['name'])
        self.assertEqual(self.new_item_response['description'],data['description'])
        #self.assertDictContainsSubset(self.new_item_response['item'], data['item'])
        #self.assertItemsEqual(self.new_item_response['links'], data['links'])


    def test_post_item_wrong_format(self):
        '''
        Tries to add a new item with wrong format
        '''

        print '('+self.test_post_item_wrong_format.__name__+')', self.test_post_item_wrong_format.__doc__

        resp = self.client.post(self.url,data=json.dumps(self.new_item_wrong_format),
                                headers={"Accept":"application/json","Content-Type":"application/json"})
        self.assertEquals(resp.status_code, 400)


class ItemTestCase (ResourcesAPITestCase):
    
    #ATTENTION: json.loads return unicode
    url = '/resys/api/items/1/'
    url_wrong = '/resys/api/items/23/'
    item_1_request_modified = {"template":{
          "data" : [
            {"prompt" : "", "name" : "name", "value" : "Hamboogs Cave"},
            {"prompt" : "", "name" : "description", "value" : "Master of puppets"},
            {"prompt" : "", "name" : "status", "value" : "1"}
                ]
            }}
    item_1_request_modified_wrong = {
            "template":
                {"data":
                    [
            {"prompt" : "", "name" : "name", "value" : "Hamboogs Cave"},
            {"prompt" : "", "name" : "description", "value" : "Master of puppets"}
                   ]}}
 
    @classmethod
    def setUpClass(cls):
        print 'Testing ItemTestCase'
    
    
    def test_url(self):
        '''
        Checks that the URL points to the right resource
        '''
        #NOTE: self.shortDescription() shuould work.
        print '('+self.test_url.__name__+')', self.test_url.__doc__
        with resources.app.test_request_context(self.url):
            rule = flask.request.url_rule
            view_point = resources.app.view_functions[rule.endpoint].view_class
            self.assertEquals(view_point, resources.Item)
    
    def test_wrong_url(self):
        '''
        Checks that GET Item returns correct status code if given a wrong item id
        '''
        print '('+self.test_wrong_url.__name__+')', self.test_wrong_url.__doc__
        resp = self.client.get(self.url_wrong)
        self.assertEquals(resp.status_code, 404)


    def test_get_item(self):
        '''
        Checks that GET Item returns correct status code and data format
        '''
        print '('+self.test_get_item.__name__+')', self.test_get_item.__doc__
        with resources.app.test_client() as client:
            resp = client.get(self.url)
            self.assertEquals(resp.status_code ,200)
            data = json.loads(resp.data)
            #The data is formed by links and item
            links = data['_links']
            #item = data ['item']

            #Check that the link format is correct
            self.assertEquals(len(links), 3)
            attr = ['collecton','self','reservations']
            for attribute in ('collection','self','reservations'):
                self.assertIn(attribute,links)

            
            #Check that the item contains all required attributes
            for attribute in ('itemID', 'name', 'description', 'status'):
                self.assertIn(attribute, data)

    def test_modify_item(self):
        '''
        Modify an existing item and check that the item has been modified correctly in the server
        '''
        print '('+self.test_modify_item.__name__+')', self.test_modify_item.__doc__
        resp = self.client.put(self.url, 
                data=json.dumps(self.item_1_request_modified), 
                headers={'Accept':'application/json','Content-Type':'application/json'})
        self.assertEquals(resp.status_code, 204)
        #Check that the message has been modified
        resp2 = self.client.get(self.url)
        self.assertEquals(resp2.status_code, 200)
        data = json.loads(resp2.data)
        #Check that the title and the body of the message has been modified with the new data
        self.assertEquals(u"Hamboogs Cave", data['name'])
        #self.assertEquals(data['message']['title'],message_1_request)

    def test_modify_unexisting_item(self):
        '''
        Try to modify an item that does not exist
        '''
        print '('+self.test_modify_unexisting_item.__name__+')', self.test_modify_unexisting_item.__doc__
        resp = self.client.put(self.url_wrong,
                                data=json.dumps(self.item_1_request_modified),
                                headers={"Content-Type":"application/json"})
        self.assertEquals(resp.status_code, 404)

    def test_modify_wrong_item(self):
        '''
        Try to modify a item sending wrong data
        '''
        print '('+self.test_modify_wrong_item.__name__+')', self.test_modify_wrong_item.__doc__
        resp = self.client.put(self.url,
                                data=json.dumps(self.item_1_request_modified_wrong),
                                headers={"Content-Type":"application/json"})
        self.assertEquals(resp.status_code, 400)

    def test_delete_item(self):
        '''
        Checks that Delete Item return correct status code if deleted correctly
        '''
        print '('+self.test_delete_item.__name__+')', self.test_delete_item.__doc__
        resp = self.client.delete(self.url)
        self.assertEquals(resp.status_code, 204)
        resp2 = self.client.get(self.url)
        self.assertEquals(resp2.status_code, 404)

    def test_delete_unexisting_item(self):
        '''
        Checks that Delete item return correct status code if given a wrong address
        '''
        print '('+self.test_delete_unexisting_item.__name__+')', self.test_delete_unexisting_item.__doc__
        resp = self.client.delete(self.url_wrong)
        self.assertEquals(resp.status_code, 404)

if __name__ == '__main__':
    print 'Start running tests'
    unittest.main()
