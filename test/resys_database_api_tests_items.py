# Created by Ivan
# Modified by Sampsa 4.8.2015
#
import sqlite3, unittest

from .resys_database_api_tests_common import BaseTestCase, db, db_path

class UserDbAPITestCase(BaseTestCase):
    
    #the strip function removes the tabs generated.
   
    no_user_nickname = 'Batty'
    initial_size = 3
    item1_id = 1
    item1_name = 'Hampooko cave'
    item1 = {'item':
                    {
                        'name':'Hampooko cave',                        
                        'description':'12m2 of pure joy. Multiple account of snus use',
                        'status':0,
                        'id':1
                        
                    }
            }
    modified_item1 = {
                        'name':'Hampookon perse',                        
                        'description':'1 m2 of pure joy. Multiple account of anus use',
                        'status':1
                     }  
                        
                    
                
      
    
    
    item2_id = 2
    item2_name = 'TS135' 
    
    
    new_item_id = 4
    new_item = {'item':
                       {
                            'user_id' : 4,
                            'useraccount':'leemola',
                            'firstname':'keijo',
                            'lastname':'seos',
                            'email':'leemo@lee.le',
                            'mobile':'112',
                            'active':0
                        }
                }
                

                
    new_item_name = {
                    'name':'leemolan luola',
                    'status':0,
                    'description':'seosta on'
                    }
            
   
            
    @classmethod
    
    def setUpClass(cls):
        print "Testing ", cls.__name__

    
    def test_items_table_created(self):
        '''
        Checks that the table initially contains 3 items (check 
        resys_data_dump.sql)
        '''
        print '('+self.test_items_table_created.__name__+')', \
              self.test_items_table_created.__doc__
        #Create the SQL Statement
        keys_on = 'PRAGMA foreign_keys = ON'
        query1 = 'SELECT * FROM items'
        #Connects to the database.
        con = sqlite3.connect(db_path)
        with con:
            #Cursor and row initialization
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            #Provide support for foreign keys
            cur.execute(keys_on)
            #Execute main SQL Statement        
            cur.execute(query1)
            items = cur.fetchall()
            #Assert
            self.assertEquals(len(items), self.initial_size)
        if con:
            con.close()
            
    def test_AddItem(self):
        '''
        Test that adding new items works properly
        '''
        print '('+self.test_AddItem.__name__+')', \
              self.test_AddItem.__doc__
        item_id = db.AddItem(self.new_item_name)
        self.assertIsNotNone(item_id)
        self.assertEquals(item_id, self.new_item_id)
        resp2 = db.GetItem(item_id)
        
        self.assertEquals(self.new_item_id, resp2['item']['id'])
            
    def test_GetItemID(self):
        '''
        Test that GetItemID returns the right value for a given item name
        '''
        print '('+self.test_GetItemID.__name__+')', \
              self.test_GetItemID.__doc__
        id = db.GetItemID(self.item1_name)
        self.assertEquals(self.item1_id, id)        
        id = db.GetItemID(self.item2_name)
        self.assertEquals(self.item2_id, id)   
        
    def test_GetItem(self):
        '''
        Test getItem with item_id == 1
        '''
        print '('+self.test_GetItem.__name__+')', \
              self.test_GetItem.__doc__
        #Test with an existing item
        item = db.GetItem(self.item1_id)
        print item
        self.assertDictContainsSubset(item, self.item1)
        #user = db.get_user(self.user2_nickname)
        #self.assertDictContainsSubset(user, self.user2)  

    def test_get_items(self):
        '''
        Test that get_items work correctly and extract required info
        '''
        print '('+self.test_get_items.__name__+')', \
              self.test_get_items.__doc__
        items = db.GetItems()
        #Check that the size is correct
        self.assertEquals(len(items), self.initial_size)
        #Iterate throug items and check if the items with item1_id and
        #item2_id are correct:
        for item in items:
            if item == self.item1:
                self.assertDictContainsSubset(item, self.item1)
                
    def test_delete_item(self):
        '''
        Test that the item id == 1 is deleted
        '''
        print '('+self.test_delete_item.__name__+')', \
              self.test_delete_item.__doc__
        resp = db.DeleteItem(self.item1_id)
        self.assertTrue(resp)
        #Check that the reservation has been really deleted through a get
        resp2 = db.GetItemID(self.item1_id)
        self.assertIsNone(resp2)    

    def test_modify_item(self):
        '''
        Test that Hampookoluola item is modifed
        '''
        print '('+self.test_modify_item.__name__+')', \
              self.test_modify_item.__doc__
        #Get and modify item
        resp = db.ModifyItem(self.item1_id, self.modified_item1)
        #Check modifying is successfull
        self.assertIsNone(resp)
        #Doublecheck trgouh get
        resp2 = db.GetItem(self.item1_id)
        resp_profile = resp2['item']
        #resp_r_profile = resp2['restricted_profile']
        #Check the expected values
        p_profile = self.modified_item1
        self.assertEquals(p_profile['name'], 
                       resp_profile['name'])
        self.assertEquals(p_profile['status'], 
                       resp_profile['status'])
        self.assertEquals(p_profile['description'], 
                       resp_profile['description'])
                
        
if __name__ == '__main__':
    print 'Start running tests'
    unittest.main()