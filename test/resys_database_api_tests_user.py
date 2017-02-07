# Created by Ivan
# Modified by Sampsa 4.8.2015

import sqlite3, unittest

from .resys_database_api_tests_common import BaseTestCase, db, db_path

class UserDbAPITestCase(BaseTestCase):
    
    #the strip function removes the tabs generated.
    
	
    no_user_nickname = 'Batty'
    initial_size = 3
	
    #Profiles used in testing:
    
    user1_id = 1
    user1_nickname = 'sampooko'
    user1 = {'user':
                    {
                        'user_id':1,
                        'useraccount':'sampooko',
                        'firstname':'Sampus',
                        'lastname':'Huuskus',
                        'email':'sboh@gboh.de',
                        'mobile':'0401234567',
                        'active':1
                    }
            }
    modified_user1 = {'user':
                            {
                                'user_id':1,
                                'useraccount':'sampooko',
                                'firstname':'Sampsa',
                                'lastname':'Huusko',
                                'email':'sampsa@huusko.com',
                                'mobile':'123456789',
                                'active':0
                            }
                    }
    
    user2_id = 2
    user2_nickname = 'jorge' 
    
    
    new_user_id = 4
    new_user = {'user':
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
                

                
    new_user_nickname = {
                            'useraccount':'leemola',
                            'firstname':'keijo',
                            'lastname':'seos',
                            'email':'leemo@lee.le',
                            'mobile':'112',
                            'active':0
                        }
            
    new_user_nickname2 = {
                            'useraccount':'sampooko',
                            'firstname':'keijo',
                            'lastname':'seos',
                            'email':'leemo@lee.le',
                            'mobile':'112',
                            'active':0
                        }
                    
            
    @classmethod
    
    def setUpClass(cls):
        print "Testing ", cls.__name__

    
    def test_users_table_created(self):
        '''
        Checks that the table initially contains 3 users (check 
        resys_data_dump.sql)
        '''
        print '('+self.test_users_table_created.__name__+')', \
              self.test_users_table_created.__doc__
        #Create the SQL Statement
        keys_on = 'PRAGMA foreign_keys = ON'
        query1 = 'SELECT * FROM users'
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
            users = cur.fetchall()
            #Assert
            self.assertEquals(len(users), self.initial_size)
            #Check the users_profile:
        if con:
            con.close()
            
    
            
    def test_GetUserID(self):
        '''
        Test that GetUserId returns the right value given a nickname
        '''
        print '('+self.test_GetUserID.__name__+')', \
              self.test_GetUserID.__doc__
        id = db.GetUserID(self.user1_nickname)
        self.assertEquals(self.user1_id, id)        
        id = db.GetUserID(self.user2_nickname)
        self.assertEquals(self.user2_id, id)
            
    def test_get_user(self):
        '''
        Test get_user with name Sampus 
        '''
        print '('+self.test_get_user.__name__+')', \
              self.test_get_user.__doc__
        #Test with an existing user
        user = db.GetUser(self.user1_nickname)
        #print user
        self.assertDictContainsSubset(user, self.user1)
        #user = db.get_user(self.user2_nickname)
        #self.assertDictContainsSubset(user, self.user2)
        
    def test_get_user_noexistingid(self):
        '''
        Test get_user with  msg-200 (no-existing)
        '''
        print '('+self.test_get_user_noexistingid.__name__+')', \
              self.test_get_user_noexistingid.__doc__
        #Test with an existing user
        user = db.GetUser(self.no_user_nickname)
        self.assertIsNone(user)
        
    def test_get_users(self):
        '''
        Test that get_users work correctly and extract required user info
        '''
        print '('+self.test_get_users.__name__+')', \
              self.test_get_users.__doc__
        users = db.GetUsers()
        #Check that the size is correct
        self.assertEquals(len(users), self.initial_size)
        #Iterate throug users and check if the users with user1_id and
        #user2_id are correct:
        for user in users:
            if user == self.user1_nickname:
                self.assertDictContainsSubset(user, self.user1)
            elif user == self.user2_nickname:
                self.assertDictContainsSubset(user, self.user2)
    
         
    def test_delete_user(self):
        '''
        #Test that the userID = 1 (sampooko) is deleted
        '''
        print '('+self.test_delete_user.__name__+')', \
              self.test_delete_user.__doc__
        resp = db.DeleteUser(self.user1_id)
        #self.assertTrue(resp)
        #Check that the users has been really deleted throug a get
        #resp2 = db.GetUser(self.user1_id)
        #self.assertIsNone(resp2)
	
    def test_modify_user(self):
        '''
        Test that the user Sampooko is modifed
        '''
        print '('+self.test_modify_user.__name__+')', \
              self.test_modify_user.__doc__
        #Get the modified user
        resp = db.ModifyUser(self.user1_nickname, self.modified_user1)
        self.assertEquals(resp, self.user1_nickname)
        #Check that the users has been really modified through a get
        resp2 = db.GetUser(self.user1_nickname)
        resp_profile = resp2['user']
        #resp_r_profile = resp2['restricted_profile']
        #Check the expected values
        p_profile = self.modified_user1['user']
        #r_profile = self.modified_user1['restricted_profile']
        self.assertEquals(p_profile['email'], 
                       resp_profile['email']) 
        self.assertEquals(p_profile['firstname'], 
                       resp_profile['firstname'])
        self.assertEquals(p_profile['lastname'], 
                       resp_profile['lastname'])
        self.assertEquals(p_profile['active'], 
                       resp_profile['active'])
        self.assertEquals(p_profile['mobile'], 
                       resp_profile['mobile']) 
        self.assertDictContainsSubset(resp2, self.modified_user1)
        
    def test_modify_user_noexistingnickname(self):
        '''
        Test modify_user with  user Batty (no-existing)
        '''
        print '('+self.test_modify_user_noexistingnickname.__name__+')', \
              self.test_modify_user_noexistingnickname.__doc__
        #Test with an existing user
        resp = db.ModifyUser(self.no_user_nickname, self.user1)
        self.assertIsNone(resp)
        
    def test_append_user(self):
        '''
        Test that I can add new users
        '''
        print '('+self.test_append_user.__name__+')', \
              self.test_append_user.__doc__
        user_id = db.AddUser(self.new_user_nickname)
        self.assertIsNotNone(user_id)
        self.assertEquals(user_id, self.new_user_id)
        #Check that the messages has been really modified through a get
        resp2 = db.GetUser(db.GetUserAccount(user_id))
        self.assertDictContainsSubset(self.new_user['user'], resp2['user'])
        
    def test_append_existing_user(self):
        '''
        Test that I cannot add two users with the same name
        '''
        print '('+self.test_append_existing_user.__name__+')', \
              self.test_append_existing_user.__doc__
        nickname = db.AddUser(self.new_user_nickname2)
        self.assertEquals(nickname, -1)
        
    def test_get_user_id(self):
        '''
        Test that get_user_id returns the right value given a nickname
        '''
        print '('+self.test_get_user_id.__name__+')', \
              self.test_get_user_id.__doc__
        id = db.GetUserID(self.user1_nickname)
        self.assertEquals(self.user1_id, id)        
        id = db.GetUserID(self.user2_nickname)
        self.assertEquals(self.user2_id, id)

    def test_get_user_id_unknown_user(self):
        '''
        Test that get_user_id returns None when the nickname does not exist
        '''
        print '('+self.test_get_user_id.__name__+')', \
              self.test_get_user_id.__doc__
        id = db.GetUserID(self.no_user_nickname)
        self.assertIsNone(id)  
    	
if __name__ == '__main__':
    print 'Start running tests'
    unittest.main()