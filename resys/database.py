'''
Created on 13.02.2013
Modified on 17.06.2015
Provides the database API to access ReSyS. 
Based on the database.py made by: ivan
Modified by Lauri Lehto
'''

from datetime import datetime
import time, sqlite3, sys, re, os
#Default paths for .db and .sql files to create and populate the database.
DEFAULT_DB_PATH = 'db/resys.db'
DEFAULT_SCHEMA = "db/resys_schema_dump.sql"
DEFAULT_DATA_DUMP = "db/resys_data_dump.sql"

class ResysDatabase(object):
    '''
    API to access ReSyS database. 
    '''
    

    def __init__(self, db_path=None):
        '''
        db_path is the address of the path with respect to the calling script.
        If db_path is None, DEFAULT_DB_PATH is used instead.
        '''
        super(ResysDatabase, self).__init__()
        if db_path is not None:
            self.db_path = db_path
        else:
            self.db_path = DEFAULT_DB_PATH


    #Setting up the database. Used for the tests.
    #SETUP, POPULATE and DELETE the database
    def clean(self):
        '''
        Purge the database removing old values.
        '''
        os.remove(self.db_path)

    def load_init_values(self, schema=None, dump=None):
        '''
        Create the database and populate it with initial values. The schema 
        argument defines the location of the schema sql file while the dump
        argument defines the location of the data dump sql file. If no value
        is provided default values are defined by the global variables 
        DEFAULT_SCHEMA and DEFAULT_DATA_DUMP
        ''' 
        #TODO Does not work, need to create *.sql and dump files
        self.create_tables_from_schema(schema)
        self.load_table_values_from_dump(dump)

    def create_tables_from_schema(self, schema=None):
        '''
        Create programmatically the tables from a schema file.
        schema contains the path to the .sql schema file. If it is None,  
        DEFAULT_SCHEMA is used instead. 
        '''
        con = sqlite3.connect(self.db_path)
        if schema is None:
            schema = DEFAULT_SCHEMA
        with open (schema) as f:
            sql = f.read()
            cur = con.cursor()
            cur.executescript(sql)

    def load_table_values_from_dump(self, dump=None):
        '''
        Populate programmatically the tables from a dump file.
        dump is the  path to the .sql dump file. If it is None,  
        DEFAULT_DATA_DUMP is used instead.
        '''
        con = sqlite3.connect(self.db_path)
        if dump is None:
            dump = DEFAULT_DATA_DUMP
        with open (dump) as f:
            sql = f.read()
            cur = con.cursor()
            cur.executescript(sql)  

    #CREATE THE TABLES PROGRAMMATICALLY WITHOUT USING SQL SCRIPT
    def CreateUsersTable(self):
        #Create profile table for users
        keys_on = 'PRAGMA foreign_keys = ON'
        stmnt = "Create table users (\
            user_id integer primary key autoincrement,\
            useraccount text,\
            firstname text,\
            lastname text,\
            email text,\
            mobile text,\
            active integer,\
            unique(useraccount,email)\
            ) "
        con = sqlite3.connect(self.db_path)
        with con:
            #Get the cursor object. 
            #It allows to execute SQL code and traverse the result set
            cur = con.cursor()
            try:
                cur.execute(keys_on)
                #execute the statement
                cur.execute(stmnt)
            except sqlite3.Error, excp:
                print "Error %s:" % excp.args[0]
        return None

    def CreateAdminTable(self):
        #Create table to hold admin users
        keys_on = 'PRAGMA foreign_keys = ON'
        stmnt = "CREATE TABLE admins (\
            user_id INTEGER,\
            PRIMARY KEY(user_id),\
            FOREIGN KEY(user_id) REFERENCES users(user_id)\
            )"
        con = sqlite3.connect(self.db_path)
        with con:
            #Get the cursor object. 
            #It allows to execute SQL code and traverse the result set
            cur = con.cursor()
            try:
                cur.execute(keys_on)
                #execute the statement
                cur.execute(stmnt)
            except sqlite3.Error, excp:
                print "Error %s:" % excp.args[0]
        return None



    def CreateItemsTable(self):
        #create Item table
        keys_on = 'PRAGMA foreign_keys = ON'
        stmnt = "CREATE TABLE items (\
            id integer primary key autoincrement,\
            name text,\
            status int,\
            description text\
            )"
        con = sqlite3.connect(self.db_path)
        with con:
            #Get the cursor object. 
            #It allows to execute SQL code and traverse the result set
            cur = con.cursor()
            try:
                cur.execute(keys_on)
                #execute the statement
                cur.execute(stmnt)
            except sqlite3.Error, excp:
                print "Error %s:" % excp.args[0]
        return None



    def CreateReservationsTable(self):
        #Table which holds reservations
        keys_on = 'PRAGMA foreign_keys = ON'
        stmnt = "CREATE TABLE reservations (\
            id integer primary key autoincrement,\
            item integer,\
            user integer,\
            ldate integer,\
            rdate integer,\
            foreign key(user) references users(user_id),\
            foreign key(item) references items(id)\
            )"
        print "Created table reservation."
        con = sqlite3.connect(self.db_path)
        with con:
            #Get the cursor object. 
            #It allows to execute SQL code and traverse the result set
            cur = con.cursor()
            try:
                cur.execute(keys_on)
                #execute the statement
                cur.execute(stmnt)
            except sqlite3.Error, excp:
                print "Error %s:" % excp.args[0]
        return None


    def create_all_tables(self):
        '''
        Create all tables programmatically, without using an external sql.
        It prints error messages in console if any of the tables could not be
        created.
        '''
        self.CreateUsersTable()
        self.CreateAdminTable()
        self.CreateItemsTable()
        self.CreateReservationsTable()
    
    #HELPERS
    def check_foreign_keys_status(self):
        '''
        Check if the foreign keys has been activated. Return and print in the
        screen if foreign keys are activated. 
        '''
        con = None
        try:
            #Connects to the database.
            con = sqlite3.connect(self.db_path)
            #Get the cursor object. 
            #It allows to execute SQL code and traverse the result set
            cur = con.cursor()    
            #Execute the pragma command
            cur.execute('PRAGMA foreign_keys')
            #We know we retrieve just one record: use fetchone()
            data = cur.fetchone()
            data_text = 'ON' if data == (1,) else 'OFF'            
            print "Foreign Keys status: %s" % data_text                
            
        except sqlite3.Error, excp:
            print "Error %s:" % excp.args[0]
            sys.exit(1)
            
        finally:
            if con:
                con.close()
        return data

    def set_and_check_foreign_keys_status(self):
        '''
        Activate the support for foreign keys and later check that the support
        exists. Print the results of this test. 
        '''
        keys_on = 'PRAGMA foreign_keys = ON'
        con = None
        try:
            #connects to the database. 
            con = sqlite3.connect(self.db_path)
            #Get the cursor object. 
            #It allows to execute SQL code and traverse the result set
            cur = con.cursor()
            #execute the pragma command, ON 
            cur.execute(keys_on)
            #execute the pragma check command
            cur.execute('PRAGMA foreign_keys')
            #we know we retrieve just one record: use ftchone()
            data = cur.fetchone()
            data_text = 'ON' if data == (1,) else 'OFF'            
            print "Foreign Keys status: %s" % data_text
            
        except sqlite3.Error, excp:
            print "Error %s:" % excp.args[0]
            sys.exit(1)
            
        finally:
            if con:
                con.close()
        return data

    
    
    #ACCESSING THE USERS TABLE
    def AddUser(self, user):
        """
        Adds a user to the database.
        INPUT:
             - user: a dictionary with the information to be modified. The
               dictionary uses following structure:
        {'useraccount':'','firstname':'','lastname':'','email':'','mobile':'','active':''}
             WHERE
             - email: New email address to set
             - useraccount: account used to log in the system
             - firstname: New firstname
             - lastname: New lastname
             - mobile: New mobile number
             - active: 0 for not active, 1 for active account
        OUTPUT:
            - Returns user_id if successful, -1 if useraccount already taken,\
                -2 if email already in use
        """
        #Create SQL statements
        #Foreign keys
        keys_on = 'PRAGMA foreign_keys = ON'
        #Query to check if useraccount exists
        query1 = 'SELECT user_id FROM users WHERE useraccount = ?'
        #Check for email
        query2 = 'SELECT user_id FROM users WHERE email = ?'
        #Create a row in users table
        query3 = 'INSERT INTO users (useraccount, email, firstname,\
                    lastname, mobile, active) VALUES(?,?,?,?,?,?)'

        #Temporary stuff
        _useraccount = user.get('useraccount',None)
        _firstname = user.get('firstname',None)
        _lastname = user.get('lastname',None)
        _email = user.get('email',None)
        _mobile = user.get('mobile',None)
        _active = user.get('active',None)
        con = sqlite3.connect(self.db_path)
        with con:
            #Cursor and row initialization
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            #Provide support for foreign keys
            cur.execute(keys_on)        
            #Execute first SQL Statement
            pvalue = (_useraccount,)
            cur.execute(query1, pvalue)
            #no value is expected
            row = cur.fetchone()
            if row is None:
                #Check if email is in use
                pvalue = (_email,)
                cur.execute(query2, pvalue)
                row = cur.fetchone()
                if row is None:
                    #Add row to users table
                    pvalue = (_useraccount,_email,_firstname,\
                        _lastname,_mobile,_active)
                    cur.execute(query3, pvalue)
                    pvalue = (_useraccount,)
                    cur.execute(query1,pvalue)
                    user = cur.fetchone()
                    #Return user_id for successful user add
                    return user['user_id']
                else:
                    #Return -2, meaning email is in use
                    return -2
            else:
                #Return -1, meaning useraccount already in use
                return -1
    

    def GetUsers(self):
        """
        Displays the contents of Users table
        INPUT:
            None
        OUTPUT:
            List of dictionaries in the following format:
            [{'user':{'user_id':'','useraccount':'','active':''},...]
            WHERE:
            - user_id: ID of the user
            - useraccount: account of the user
            - active: if user is active or not
        """

        keys_on = 'PRAGMA foreign_keys = ON'
        query1 = 'SELECT * FROM users'
        con = sqlite3.connect(self.db_path)
        with con:
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            cur.execute(keys_on)
            cur.execute(query1)
            rows = cur.fetchall()
            #print rows
            if rows is None:
                return None
            users = []
            for row in rows:
                users.append(self._create_user_object(row))
                #users.append({'user':{'user_id':row['user_id'],'useraccount':row['useraccount'],'active':row['active']}})
            return users

    def GetUser(self, useraccount):
        """
        Gets a single users information
        INPUT:
            - useraccount: account which the user logs on
        OUTPUT:
            Dictionary in following format:
            {'user':{'user_id':'','useraccount':'','firstname':'',
                                'lastname':'','email':'',
                                'mobile':'','active':''
                                  }
            }
            WHERE:
             - user_id: user ID in the database
             - useraccount: account chosen by the user
             - firstname: first name of the user
             - lastname: last name of the user
             - email: current email of the user.
             - mobile: phone number of the user
             - active: status of activation, 1 is active, 0 not
        """

        keys_on = 'PRAGMA foreign_keys = ON'
        query1 = 'SELECT user_id FROM users WHERE useraccount = ?'
        query2 = 'SELECT * FROM users WHERE user_id = ?'
        con = sqlite3.connect(self.db_path)
        with con:
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            cur.execute(keys_on)
            pvalue = (useraccount,)
            cur.execute(query1,pvalue)
            
            row = cur.fetchone()
            if row is None:
                return None
            user_id = row["user_id"]
            #print user_id
            pvalue = (user_id,)
            cur.execute(query2, pvalue)
            user = cur.fetchone()
            #print user
            return self._create_user_object(user)

    def GetUserAccount(self, uid):
        """
        INPUT:
            uid: user ID
        OUTPUT:
            useraccount
        """
        
        keys_on = 'PRAGMA foreign_keys = ON'
        query2 = 'SELECT * FROM users WHERE user_id = ?'
        con = sqlite3.connect(self.db_path)
        with con:
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            cur.execute(keys_on)
            pvalue = (uid,)
            cur.execute(query2, pvalue)
            user = cur.fetchone()
            #print user
            return user["useraccount"]

    def ModifyUser(self, useraccount, user_row):

        """
        Modifies the user useraccount.
        INPUT:
             - useraccount: Account to modify
             - user: a dictionary with the information to be modified. The
               dictionary uses following structure:

            {'user':{'user_id':'','useraccount':'','firstname':'',
                                'lastname':'','email':'',
                                'mobile':'','active':''
                                  }
            }
             WHERE
             - email: New email address to set
             - firstname: New firstname
             - lastname: New lastname
             - mobile: New mobile number
             - active: 0 for not active, 1 for active account

        OUTPUT:
            Return 0 if the update was successful or None if useraccount was not found.

        """
        keys_on = 'PRAGMA foreign_keys = ON'
        #Extract userid
        query1 = 'SELECT user_id FROM users WHERE useraccount = ?'
        #update user
        query2 = 'UPDATE users SET email = ?, firstname = ?, lastname = ?,\
                    mobile = ?, active = ?\
                    WHERE user_id = ?'
        #Temporary stuff
        user = user_row
        _firstname = user.get('firstname',None)
        _lastname = user.get('lastname',None)
        _email = user.get('email',None)
        _mobile = user.get('mobile',None)
        _active = user.get('active',None)

        con = sqlite3.connect(self.db_path)
        with con:
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            cur.execute(keys_on)
            pvalue = (useraccount,)
            cur.execute(query1, pvalue)
            row = cur.fetchone()
            if row is None:
                return None
            else:
                user_id = row["user_id"]
                pvalue = (_email, _firstname, _lastname, _mobile, _active, user_id)
                cur.execute(query2, pvalue)
                if cur.rowcount < 1:
                    return None
                return useraccount

    def GetUserID(self, useraccount):
        """
        INPUT:
            - Useraccount: accunt of the user
        OUTPUT:

            - Returns the user_id of useraccount if succesful,
            else None.
        """
        keys_on = 'PRAGMA foreign_keys = ON'
        #Extract userid
        query1 = 'SELECT user_id FROM users WHERE useraccount = ?'
        
        con = sqlite3.connect(self.db_path)
        with con:
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            cur.execute(keys_on)
            pvalue = (useraccount,)
            cur.execute(query1, pvalue)
            row = cur.fetchone()
            if row is None:
                return None
            else:
                user_id = row["user_id"]
                return user_id
    def ContainsUser(self, useraccount):
        """
        Returns true if useraccount is in the system
        """
        return self.GetUserID(useraccount.lower()) is not None

    def DeleteUser(self, uid):
        """
        Delete user from database
        INPUT:
            - uid: user_id
        Output:
            - None if the user is deleted, 1 otherwise
        """
        keys_on = 'PRAGMA foreign_keys = ON'
        #Extract userid
        query1 = 'DELETE FROM users WHERE user_id = ?'
        
        con = sqlite3.connect(self.db_path)
        with con:
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            cur.execute(keys_on)
            pvalue = (uid,)
            cur.execute(query1, pvalue)

            if cur.rowcount < 1:
                return 1
            return None


    def _create_user_object(self, row):
        '''
        Takes a database Row and transforms it into a python dictionary.
        Dictionary has the following format:
            {'user':{'user_id':'','useraccount':'','firstname':'',
                                'lastname':'','email':'',
                                'mobile':'','active':''
                                  }
            }
            where:
             - user_id: user ID in the database
             - useraccount: account chosen by the user
             - firstname: first name of the user
             - lastname: last name of the user
             - email: current email of the user.
             - mobile: phone number of the user
             - active: status of activation, 1 is active, 0 not
        Note that all values are string if they are not otherwise indicated.
        '''
        return {'user_id':row['user_id'],
                            'useraccount':row['useraccount'],
                            'firstname':row['firstname'],
                            'lastname':row['lastname'],
                            'email':row['email'], 
                            'mobile':row['mobile'],
                            'active':row['active'],        
               }






    #Functions for admin table
    #Add an dmin
    def AddAdmin(self, uid):
        """
        Adds an admin to the table
        INPUT:
            - uid : user_id of the person who is given admin rights
        OUTPUT:
            - 0 if successful
            - None if user_id doesnt exist
        """
        
        keys_on = 'PRAGMA foreign_keys = ON'
        #check userid
        query1 = 'SELECT * FROM users WHERE user_id = ?'
        #add admin
        query2 = 'INSERT INTO admins VALUES(?)'

        con = sqlite3.connect(self.db_path)
        with con:
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            cur.execute(keys_on)
            pvalue = (uid,)
            cur.execute(query1, pvalue)
            row = cur.fetchone()
            if row is None:
                return None
            else:
                cur.execute(query2, pvalue)
                return uid

    def ShowAdmins(self):
        """
        Show all admins
        INPUT:
            -None
        OUTPUT:
            - Tuple consisting of Useraccount and user_id
        """

        keys_on = 'PRAGMA foreign_keys = ON'
        query1 = 'SELECT users.useraccount, admins.user_id from users, admins WHERE users.user_id = admins.user_id'
        
        con = sqlite3.connect(self.db_path)
        with con:
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            cur.execute(keys_on)
            cur.execute(query1)
            rows = cur.fetchall()
            #print rows
            if rows is None:
                return None
            admins = []
            for row in rows:
                admins.append(row)
            return admins

    def DeleteAdmin(self, uid):
        """
        )Deletes an admin
        INPUT:
            -uid: user_id of the admin to delete
        OUTPUT:
            0 if succesful, else 1
        """

        keys_on = 'PRAGMA foreign_keys = ON'
        #check userid
        query1 = 'DELETE FROM admins WHERE user_id = ?'

        con = sqlite3.connect(self.db_path)
        with con:
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            cur.execute(keys_on)
            pvalue = (uid,)
            cur.execute(query1, pvalue)
            if cur.rowcount < 1:
                return 1
            return 0


    #ITEM TABLE FUNCTIONS

    def AddItem(self, item):
        """
        Adds an item to database
        INPUT:
            - item: Dictioary with following structuce:
              {
                'name':'',
                'status':'',
                'description':''
              }
        OUTPUT
            Item ID is successful,-1 if name taken, else None
        """


        #Create SQL statements
        #Foreign keys
        keys_on = 'PRAGMA foreign_keys = ON'
        #Create a row in items table
        query1 = 'INSERT INTO items (name, status, description) VALUES(?,?,?)'
        query2 = 'SELECT * FROM items WHERE name = ?'

        #Temporary stuff
        _name= item.get('name',None)
        _status = item.get('status',None)
        _description = item.get('description',None)
        con = sqlite3.connect(self.db_path)
        with con:
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            cur.execute(keys_on)        

            pvalue = (_name,)
            cur.execute(query2,pvalue)
            row = cur.fetchone()
            if row is None:
                pvalue = (_name,_status,_description)
                cur.execute(query1, pvalue)
                if cur.rowcount > 0:
                    pvalue = (_name,)
                    cur.execute(query2,pvalue)
                    item = cur.fetchone()
                    if item is None:
                        return None
                    else:
                        return item['id']
            return -1
    
    
    def GetItemID(self, name):
        """
        Return item_id of an item with given name
        INPUT:
            - name: name of the item 

        OUTPUT:
            - ID of the item
        """

        keys_on = 'PRAGMA foreign_keys = ON'
        #Extract userid
        query1 = 'SELECT id FROM items WHERE name = ?'
        
        con = sqlite3.connect(self.db_path)
        with con:
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            cur.execute(keys_on)
            pvalue = (name,)
            cur.execute(query1, pvalue)
            row = cur.fetchone()
            if row is None:
                return None
            else:
                item_id = row["id"]
                return item_id


    def GetItem(self, item_id):
        """
        Returns an items information
        INPUT:
            - item_id: id of the item 

        OUTPUT:
            Dictionary containing item data in the format
            {'item':{'id':'', 'name':'', 'status':'','description':''}}
            Returns None if get fails            
        """
        
        keys_on = 'PRAGMA foreign_keys = ON'
        query1 = 'SELECT * FROM items WHERE id = ?'
        con = sqlite3.connect(self.db_path)
        with con:
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            cur.execute(keys_on)
            pvalue = (item_id,)
            cur.execute(query1,pvalue)
            item = cur.fetchone()
            if item is None:
                return None
            return self._create_item_object(item)

    def _create_item_object(self, row):
        """
        Takes a database Row and transforms it into a python dictionary.
        Dictionary has the following format:
            {'item':{"name":'','id':'', 'status':'','description':''}}
            where: 
                -name: name of the item
                -id: item id
                -Status: item status
                -description: description of the item
        """
        return {"name":row['name'],
                            'id':row['id'],
                            'status':row['status'],
                            'description':row['description']
                        
                }
                

    def GetItems(self):
        """
        Finds all items on the database.
        INPUT:
            None
        OUTPUT:
            List of item dictionaries in the following form:
                [{'item':{'id':'','name':'','status':'','description':''}},
                    ...]
            If search fails, returns Nonw
        """
        
        keys_on = 'PRAGMA foreign_keys = ON'
        query1 = 'SELECT * FROM items'
        con = sqlite3.connect(self.db_path)
        with con:
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            cur.execute(keys_on)
            cur.execute(query1)
            rows = cur.fetchall()
            if rows is None:
                return None
            items = []
            for item in rows:
                items.append(self._create_item_object(item))
            return items
    
    def DeleteItem(self, item_id):
        """
        Deletes item from database.
        INPUT: 
            - item_id: ID of the item to be deleted
        OUTPUT:
            - Return None if deleting is succesfull, else 1
        """

        keys_on = 'PRAGMA foreign_keys = ON'
        #Extract userid
        query1 = 'DELETE FROM items WHERE id = ?'
        
        con = sqlite3.connect(self.db_path)
        with con:
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            cur.execute(keys_on)
            pvalue = (item_id,)
            cur.execute(query1, pvalue)

            if cur.rowcount < 1:
                return 1
            return None
    
    
    def ModifyItem(self, item_id, item):
        """
        Modifies the item contents
        INPUT:
            item id and dictionary in the form 
            {
                'name':'',
                'status':'',
                'description':''
            }
        OUTPUT:
            returns None on succesfull modify, else 1
        """
        keys_on = 'PRAGMA foreign_keys = ON'
        query1 = 'UPDATE items SET name = ?, status = ?, description = ?\
                    WHERE id = ?'
        #Temporary stuff
        _name = item.get('name',None)
        _status = item.get('status',None)
        _description = item.get('description',None)

        con = sqlite3.connect(self.db_path)
        with con:
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            cur.execute(keys_on)
            pvalue = (_name,_status,_description, item_id)
            cur.execute(query1, pvalue)
            if cur.rowcount < 1:
                return 1
            return None

    def HoldsItem(self, name):
        """
        Checks if database holds a certain item with id item_id
        Output True if it does, else False
        """
        return self.GetItemID(name) is not None


#RESERVATIONS

    def AddReservation(self, reservation):
        #item, user, ldate, rdate=None):
        """
        Adds a new reservation to user
        INPUT:
            Dictionary in the following form:
            {'item':'','user':'','ldate':'','rdate':''}
    
        WHERE
            item: Item id
            user: Useraccout
            ldate: Loan date, unix time format
            rdate: return date, default None, unix time format

        OUTPUT:
            reservation ID for successfull reservation, else None
        """

        #Create SQL statements
        #Foreign keys
        keys_on = 'PRAGMA foreign_keys = ON'
        #Create a row in items table
        query1 = 'INSERT INTO reservations (item, user, ldate, rdate) VALUES(?,?,?,?)'
        #Query for finding the ID of the reservation
        query2 = 'SELECT id FROM reservations WHERE user = ? AND item = ? AND ldate = ?'
        #Temporary stuff
        _item= reservation.get('item',None)
        _user= reservation.get('user',None)
        _user= self.GetUserID(_user)
        _ldate= reservation.get('ldate',None)
        _rdate= reservation.get('rdate',None)
        con = sqlite3.connect(self.db_path)
        with con:
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            cur.execute(keys_on)        

            #pvalue = (_name,)
            #cur.execute(query2,pvalue)
            #row = cur.fetchone()
            pvalue = (_item,_user,_ldate,_rdate)
            cur.execute(query1, pvalue)
            if cur.rowcount > 0:
                pvalue = (_user,_item,_ldate)
                cur.execute(query2, pvalue)
                rid = cur.fetchone()
                return rid['id']
            return None

    def ModifyReservation(self, reservation):
        #id, item , user, ldate, rdate):
        """
        Modifies the selected reservation
        INPUT:
            Dictionary in the following form:
                {'id':'','item':'','user':'','ldate':'','rdate':''}
                
        WHERE
            item: Item id
            user: User id
            ldate: Loan date, unix time format
            rdate: return date, default None, unix time format

        OUTPUT:
            reservation ID for successfull update, else None
        """

        keys_on = 'PRAGMA foreign_keys = ON'
        query1 = 'UPDATE reservations SET item = ?, user = ?, ldate = ?, rdate = ?\
                    WHERE id = ?'
        #Query for finding the ID of the reservation
        query2 = 'SELECT id FROM reservations WHERE user = ? AND item = ? AND ldate = ?'
        #Temporary stuff
        print reservation
        _id= reservation.get('id',None)
        _item= reservation.get('item',None)
        _user= reservation.get('user',None)
        #_user= self.GetUserID(_user)
        _ldate= reservation.get('ldate',None)
        _rdate= reservation.get('rdate',None)

        con = sqlite3.connect(self.db_path)
        with con:
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            cur.execute(keys_on)
            pvalue = (_item,_user,_ldate, _rdate,_id)
            cur.execute(query1, pvalue)
            if cur.rowcount < 1:
                return None
            pvalue = (_user,_item,_ldate)
            cur.execute(query2, pvalue)
            print pvalue,"sadad"
            rid = cur.fetchone()
            return rid['id']

    
    def DeleteReservation(self, id):
        """"
        Deletes the reservation with id
        INPUT: 
            id: ID of the reservation
        OUTPUT:
            1 for successfull delete, else None
        """
        
        keys_on = 'PRAGMA foreign_keys = ON'
        query1 = 'DELETE FROM reservations WHERE id = ?'
        
        con = sqlite3.connect(self.db_path)
        with con:
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            cur.execute(keys_on)
            pvalue = (id,)
            cur.execute(query1, pvalue)

            if cur.rowcount < 1:
                return None
            return 1

    def GetItemReservations(self, item):
        """
        Retrieves a certain items reservation list
        INPUT:
            user: ID of the item
        OUTPUT:
            list of reservations in the following form:
            [{'reservation':{'id':'','user':'','item':'','ldate':'','rdate':''}
                ...]
            returns None if item id doestn exist
        """

        keys_on = 'PRAGMA foreign_keys = ON'
        query1 = 'SELECT * FROM reservations WHERE item = ?'
        query2 = 'SELECT * FROM items WHERE id = ?'

        
        con = sqlite3.connect(self.db_path)
        with con:
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            cur.execute(keys_on)
            pvalue = (item,)
            cur.execute(query2, pvalue)
            if cur.fetchone() is None:
                return None
            cur.execute(query1, pvalue)
            rows = cur.fetchall()
            reservations = []
            for reservation in rows:
                reservations.append(self._create_reservation_object(reservation))
            return reservations


    def GetActiveReservations(self, user):
        """
        Retrieves a list of reservations by a certain user
        INPUT:
            user: ID of the user
        OUTPUT:
            list of reservations in the following form:
            [{'reservation':{'id':'','user':'','item':'','ldate':'','rdate':''}
                ...]
            returns None if user id doestn exist
        """

        keys_on = 'PRAGMA foreign_keys = ON'
        query1 = 'SELECT * FROM reservations WHERE user = ?'
        query2 = 'SELECT * FROM users WHERE user_id = ?'

        
        con = sqlite3.connect(self.db_path)
        with con:
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            cur.execute(keys_on)
            pvalue = (user,)
            cur.execute(query2, pvalue)
            if cur.fetchone() is None:
                return None
            cur.execute(query1, pvalue)
            rows = cur.fetchall()
            reservations = []
            for reservation in rows:
                reservations.append(self._create_reservation_object(reservation))
            return reservations

    def _create_reservation_object(self,row):
        """
        Takes a database row and returns it as a dictionary
        """
        return {'id':row['id'],
                                'user':row['user'],
                                'item':row['item'],
                                'ldate':row['ldate'],
                                'rdate':row['rdate']
                }

    def GetReservations(self):
        """
        Retrieves a list of all reservations
        """

        keys_on = 'PRAGMA foreign_keys = ON'
        query1 = 'SELECT * FROM reservations'
        #query2 = 'SELECT * FROM users WHERE user_id = ?'

        
        con = sqlite3.connect(self.db_path)
        with con:
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            cur.execute(keys_on)
            cur.execute(query1)
            rows = cur.fetchall()
            reservations = []
            for reservation in rows:
                reservations.append(self._create_reservation_object(reservation))
            return reservations
    
    
    def GetReservation(self, id):
        """
        Retrieves a list of all reservations
        """

        keys_on = 'PRAGMA foreign_keys = ON'
        query1 = 'SELECT * FROM reservations WHERE id = ?'

        
        con = sqlite3.connect(self.db_path)
        with con:
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            cur.execute(keys_on)
            pvalue = (id,)
            cur.execute(query1,pvalue)
            row = cur.fetchone()
            if row:
                reservation = self._create_reservation_object(row)
                return reservation
            return None
