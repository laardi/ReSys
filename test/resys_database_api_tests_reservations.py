import sqlite3, unittest

from .database_api_tests_common import BaseTestCase, db, db_path

class ReservationDbAPITestCase(BaseTestCase):
    '''
            The format of the Reservation dictionary is the following:
            {'id':,
             'item',
             'user':,
             'ldate':,
             'rdate':
             }
             
            where:
             - id: unique id of the reservation
             - item: unique id of the reserved item
             - user: unique id of the reserving user
             - ldate: UNIX timestamp when reservation begins
             - rdate UNIX timestamp when reservation ends

    '''

    # Reservations used in the test
    reservation1 = {'id':1,
                    'item':1,
                    'user':1,
                    'ldate':1435660760,
                    'rdate':1435661760
                    }

    m_reservation1 = {'id':1,
                    'item':1,
                    'user':1,
                    'ldate':1435661760,
                    'rdate':1435662760
                    }

    reservation2 = {'id':2,
                    'item':2,
                    'user':2,
                    'ldate':1435660860,
                    'rdate':1435662760
                    }

    no_reservation = {'id':15,
                      'item':5,
                      'user':6,
                      'ldate':1332360860,
                      'rdate':1400662760
                      }
    
    new_reservation = {'item':3,
                       'user':1,
                       'ldate':1435663760,
                       'rdate':1435664760
                       }

    
    # the initial size of the reservations table:
    initial_size = 2
 
    @classmethod
    def setUpClass(cls):
        print "Testing ", cls.__name__

    # MODIFIED TESTS FROM TEST EXAMPLES
    def test_reservations_table_created(self):
        '''
        Checks that the table initially contains 2 reservations (check 
        forum_data_dump.sql)
        '''
        print '('+self.test_reservations_table_created.__name__+')', \
              self.test_reservations_table_created.__doc__
        #Create the SQL Statement
        keys_on = 'PRAGMA foreign_keys = ON'
        query = 'SELECT * FROM reservations'
        #Connects to the database.
        con = sqlite3.connect(db_path)
        with con:
            #Cursor and row initialization
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            #Provide support for foreign keys
            cur.execute(keys_on)
            #Execute main SQL Statement        
            cur.execute(query)
            reservations = cur.fetchall()
            #Assert
            self.assertEquals(len(reservations), self.initial_size)
        if con:
            con.close()


    def test_create_reservation_object(self):
        '''
        Check that the method create_reservation_object works return adequate values
        for the first database row.
        '''
        print '('+self.test_create_reservation_object.__name__+')', \
              self.test_create_reservation_object.__doc__
        #Create the SQL Statement
        keys_on = 'PRAGMA foreign_keys = ON'
        query = 'SELECT * FROM reservations'
        #Connects to the database.
        con = sqlite3.connect(db_path)
        
        with con:
            #Cursor and row initialization
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            #Provide support for foreign keys
            cur.execute(keys_on)
            #Execute main SQL Statement        
            cur.execute(query)
            #Extract the row
            row = cur.fetchone()
            #Test the method
            #reservation = db._create_reservation_object(row)
            reservation = db._create_reservation_object(row)
            self.assertDictContainsSubset(reservation["reservation"], self.reservation1)


    def test_get_reservation(self):
        '''
        Test get_reservation
        '''
        print '('+self.test_get_reservation.__name__+')', \
              self.test_get_reservation.__doc__
        #Test with an existing reservation
        reservation = db.GetReservation(self.reservation1["id"])
        self.assertDictContainsSubset(reservation["reservation"], self.reservation1)
        reservation = db.GetReservation(self.reservation2["id"])
        self.assertDictContainsSubset(reservation["reservation"], self.reservation2)

    
    def test_get_reservation_noexistingid(self):
        '''
        Test get_reservation with id "15" (non_existent)
        '''
        print '('+self.test_get_reservation_noexistingid.__name__+')', \
              self.test_get_reservation_noexistingid.__doc__
        #Test with an existing user
        reservation = db.GetReservation(self.no_reservation["id"])
        self.assertIsNone(reservation)

    
    def test_get_reservations(self):
        '''
        Test that get_reservations work correctly and extract required reservation info
        '''
        print '('+self.test_get_reservations.__name__+')', \
              self.test_get_reservations.__doc__
        reservations = db.GetReservations()
        #Check that the size is correct
        self.assertEquals(len(reservations), self.initial_size)
        #Iterate throug users and check if the reservations with reservation1 and
        #reservation2 are correct:
        for reservation in reservations:
            if reservation["reservation"]["id"] == self.reservation1["id"]:
                self.assertDictContainsSubset(reservation["reservation"], self.reservation1)
            elif reservation["reservation"]["id"] == self.reservation2["id"]:
                self.assertDictContainsSubset(reservation["reservation"], self.reservation2)


    def test_delete_reservation(self):
        '''
        Test that the reservation is deleted
        '''
        print '('+self.test_delete_reservation.__name__+')', \
              self.test_delete_reservation.__doc__
        resp = db.DeleteReservation(self.reservation1["id"])
        self.assertTrue(resp)
        #Check that the reservation has been really deleted through a get
        resp2 = db.GetReservation(self.reservation1["id"])
        self.assertIsNone(resp2)


    def test_modify_reservation(self):
        '''
        Test that the reservation is modified
        '''
        print '('+self.test_modify_reservation.__name__+')', \
              self.test_modify_reservation.__doc__
        #Modify the reservation
        resp = db.ModifyReservation(self.m_reservation1)
        self.assertEquals(resp, self.reservation1["id"])
        #Get the modified reservation
        resp2 = db.GetReservation(self.m_reservation1["id"])
        resp2 = resp2["reservation"]
        #Check the expected values
        self.assertEquals(resp2["id"],1)
        self.assertEquals(resp2["item"],1)
        self.assertEquals(resp2["user"],1)
        self.assertEquals(resp2["ldate"],1435661760)
        self.assertEquals(resp2["rdate"],1435662760)


    def test_modify_reservation_noexistingid(self):
        '''
        Test modify_reservation with id "15" (non_existent)
        '''
        print '('+self.test_modify_reservation_noexistingid.__name__+')', \
              self.test_modify_reservation_noexistingid.__doc__
        #Test modifying the reservation
        resp = db.ModifyReservation(self.no_reservation)
        resp2 = db.GetReservation(self.no_reservation["id"])
        self.assertIsNone(resp2)


    def test_append_reservation(self):
        '''
        Test that I can add new reservations
        '''
        print '('+self.test_append_reservation.__name__+')', \
              self.test_append_reservation.__doc__
        #Add a new reservation
        reservationid = db.AddReservation(self.new_reservation)
        #Check if succesfully created (given the id)
        self.assertIsNotNone(reservationid)
        #Get the new reservation
        reservation = db.GetReservation(reservationid)
        reservation = reservation["reservation"]
        #Check if all fields succesful
        self.assertEquals(reservationid, 3)
        self.assertEquals(reservation["item"], 3)
        self.assertEquals(reservation["user"], 1)
        self.assertEquals(reservation["ldate"], 1435663760)
        self.assertEquals(reservation["rdate"], 1435664760)

    
    def test_append_existing_reservation(self):
        '''
        Test that I cannot add two reservations with the same id
        '''
        print '('+self.test_append_existing_reservation.__name__+')', \
              self.test_append_existing_reservation.__doc__
        # TO BE IMPLEMENTED LATER
        # WHEN THE FUNCTION CALL
        # IS MODIFIED
        
    def test_active_reservations(self):
        '''
        Test that all of the user's reservations show correctly
        '''
        print '('+self.test_active_reservations.__name__+')', \
              self.test_active_reservations.__doc__
        #Add a new reservation
        db.AddReservation(self.new_reservation)
        #Check the reservation count for user and compare
        count = len(db.GetActiveReservations(self.new_reservation["user"]))
        self.assertEquals(count, 2)


if __name__ == '__main__':
    print 'Start running tests'
    unittest.main()
