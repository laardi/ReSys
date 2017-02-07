#!/usr/bin/python
# -*- coding: utf_8 -*-
# RESERVATION SYSTEM CLIENT v. 0.1
# Jussi Moilanen

"""
TO DO/FIX:

- FIX UTF-8 PROBLEM (CHARACTERS LIKE ä AND ö DON'T WORK)

- BETTER ERROR HANDLING FOR POORLY WRITTEN PROGRAM AND/OR STUPID USERS (SEE: THERAC-25)

- BETTER FUNCTION NAMING, CODE COMMENTARY AND OTHER CLEAN UP

- POSSIBLE PYTHON GUI (PYTHON GUI PROGRAMMING PROVIDED TO BE QUITE DIFFICULT FOR THIS CLIENT)
  (MAYBE TKINTER?)

- POSSIBLE HTML GUI

"""

# IMPORTS
import textwrap, os, datetime, time, re, requests, json



# DEFINE FUNCTIONS

# SHOW TIME IN USER READABLE FORMAT
def formattime(giventime):
    showntime = datetime.datetime.fromtimestamp(giventime).strftime("%d.%m.%Y %H:%M")
    return showntime



# INPUT TIME IN USER READABLE FORMAT
def inputtime(giventime):
    try:
        giventime = map(int, re.sub("[^\w]", " ", giventime).split())
        timetoconvert = datetime.datetime(giventime[2], giventime[1], giventime[0], giventime[3], giventime[4])
        convertedtime = int(time.mktime(timetoconvert.timetuple()))
        return convertedtime
    except:
        return None



# USERS PAGE
def userspage():

    # HREF
    href = "http://localhost:5000/resys/api/users/"
    
    # List to save users
    users = []
    
    # Get users
    r = requests.get(href)
    json_data = json.loads(r.text)
 
    # Print users
    print "\n\nUSERS:\n%s\n---------------------------------\n" % href
    for entry in json_data["collection"]["items"]:
        users.append(entry["data"][0]["value"])
        print "USER: %s\n" % entry["data"][0]["value"]
    
    # Print commands
    print """---------------------------------
COMMANDS:

    Type username to view user information.
   
    Type 'items' to view ITEMS.
    Type 'reservations' to view RESERVATIONS.
    
    Type 'add' to ADD user.
    
    Type 'quit' to QUIT.
"""

    # Selection prompt
    while True:
        
        selection = raw_input("Selection: ")

        if selection in users:
            userpage(selection)
        elif selection == "items":
            itemspage()
        elif selection == "reservations":
            reservationspage()

        elif selection == "add":
            add("user")
            
        elif selection == "quit":
            print "Quitting program."
            os._exit(0)
            
        else:
            pass


# ITEMS PAGE
def itemspage():

    # HREF
    href = "http://localhost:5000/resys/api/items/"
    
    # List to save items
    items = []
    
    # Get users
    r = requests.get(href)
    json_data = json.loads(r.text)
 
    # Print users
    print "\n\nITEMS:\n%s\n---------------------------------\n" % href
    for entry in json_data["collection"]["items"]:
        items.append(str(entry["data"][1]["value"]))
        print "ITEM: %s - %s\n" % (entry["data"][1]["value"], entry["data"][0]["value"])
    
    # Print commands
    print """---------------------------------
COMMANDS:

    Type item ID to view item information.

    Type 'users' to view USERS.
    Type 'reservations' to view RESERVATIONS.
    
    Type 'add' to ADD item.
    
    Type 'quit' to QUIT.
"""

    # Selection prompt
    while True:
        
        selection = raw_input("Selection: ")

        if selection in items:
            itempage(selection)
        elif selection == "users":
            userspage()
        elif selection == "reservations":
            reservationspage()

        elif selection == "add":
            add("item")
            
        elif selection == "quit":
            print "Quitting program."
            os._exit(0)
            
        else:
            pass



# RESERVATIONS PAGE
def reservationspage():

    # HREF
    href = "http://localhost:5000/resys/api/reservations/"
    
    # List to save reservations
    reservations = []
    
    # Get reservations
    r = requests.get(href)
    json_data = json.loads(r.text)
 
    # Print reservations
    print "\n\nRESERVATIONS:\n%s\n---------------------------------\n" % href

    for entry in json_data["collection"]["items"]:
        reservations.append(str(entry["data"][0]["value"]))
        r = requests.get("http://localhost:5000/resys/api/items/%s/" % entry["data"][1]["value"])
        json_data2 = json.loads(r.text)
        print "RESERVATION: %s - %s\n" % (entry["data"][0]["value"], json_data2["name"])
        
    # Print commands
    print """---------------------------------
COMMANDS:

    Type reservation ID to view reservation information.

    Type 'users' to view USERS.
    Type 'items' to view ITEMS.
    
    Type 'add' to ADD reservation.
    
    Type 'quit' to QUIT.
"""

     # Selection prompt
    while True:
        
        selection = raw_input("Selection: ")

        if selection in reservations:
            reservationpage(selection)
        elif selection == "users":
            userspage()
        elif selection == "items":
            itemspage()

        elif selection == "add":
            add("reservation")
            
        elif selection == "quit":
            print "Quitting program."
            os._exit(0)
            
        else:
            pass


# INDIVIDUAL USER PAGE
def userpage(user):
    
    # HREF
    href = "http://localhost:5000/resys/api/users/%s/" % user

    # Get user information
    r = requests.get(href)
    json_data = json.loads(r.text)
    
    # Print user
    print "\n\nUSER: %s\n%s\n---------------------------------\n" % (user, href)
    print """USERNAME: %s
\nFIRST NAME: %s
\nLAST NAME: %s
\nMOBILE: %s
\nEMAIL: %s
""" % (json_data["useraccount"],
            json_data["firstname"],
            json_data["lastname"],
            "" if json_data["mobile"] == None else json_data["mobile"],
            "" if json_data["email"] == None else json_data["email"])

    # Print commands
    print """---------------------------------
COMMANDS:

    Type 'view' to view this USER'S RESERVATIONS.
    
    Type 'users' to view USERS.
    Type 'reservations' to view RESERVATIONS.
    Type 'items' to view ITEMS.
    
    Type 'modify' to MODIFY user.
    Type 'delete' to DELETE user.
    
    Type 'quit' to QUIT.
"""

    # Selection prompt
    while True:
        
        selection = raw_input("Selection: ")

        if selection == "view":
            userreservations(user)
        elif selection == "users":
            userspage()
        elif selection == "items":
            itemspage()
        elif selection == "reservations":
            reservationspage()

        elif selection == "modify":
            modify("user", href)
        elif selection == "delete":
            r = requests.delete(href)
            if r.status_code == 204:
                print "User deletion successful."
            else:
                print "User deletion not succesful, response: %s" % r.status_code
            userspage()
            
        elif selection == "quit":
            print "Quitting program."
            os._exit(0)
            
        else:
            pass



# INDIVIDUAL ITEM PAGE
def itempage(item):
    
    # HREF
    href = "http://localhost:5000/resys/api/items/%s/" % item

    # Get item information
    r = requests.get(href)
    json_data = json.loads(r.text)
    
    # Print item
    print "\n\nITEM: %s\n%s\n---------------------------------\n" % (item, href)
    print """ITEM ID: %s
\nITEM NAME: %s
\nDESCRIPTION: %s
\nSTATUS: %s
""" % (json_data["itemID"],
            json_data["name"],
            json_data["description"],
            json_data["status"])
            

    # Print commands
    print """---------------------------------
COMMANDS:

    Type 'view' to view this ITEM'S RESERVATIONS.
    
    Type 'users' to view USERS.
    Type 'reservations' to view RESERVATIONS.
    Type 'items' to view ITEMS.
    
    Type 'modify' to MODIFY item.
    Type 'delete' to DELETE item.
    
    Type 'quit' to QUIT.
"""

    # Selection prompt
    while True:
        
        selection = raw_input("Selection: ")

        if selection == "view":
            itemreservations(item)
        elif selection == "users":
            userspage()
        elif selection == "items":
            itemspage()
        elif selection == "reservations":
            reservationspage()

        elif selection == "modify":
            modify("item", href)
        elif selection == "delete":
            r = requests.delete(href)
            if r.status_code == 204:
                print "Item deletion successful."
            else:
                print "Item deletion not succesful, response: %s" % r.status_code
            itemspage()
            
        elif selection == "quit":
            print "Quitting program."
            os._exit(0)
            
        else:
            pass


# INDIVIDUAL RESERVATION PAGE
def reservationpage(reservation):
    
    # HREF
    href = "http://localhost:5000/resys/api/reservations/%s/" % reservation

    # Get item information
    r = requests.get(href)
    json_data = json.loads(r.text)
    
    r = requests.get("http://localhost:5000/resys/api/items/%s/" % json_data["item"])
    json_data2 = json.loads(r.text)
    
    # Print item
    print "\n\nRESERVATION: %s\n%s\n---------------------------------\n" % (reservation, href)
    print """RESERVATION ID: %s
\nITEM NUMBER: %s
\nITEM NAME: %s
\nUSER: %s
\nLOAN DATE: %s
\nRETURN DATE: %s
""" % (json_data["reservation_ID"],
     json_data["item"],
     json_data2["name"],
     json_data["user"],
     formattime(json_data["ldate"]),
     "" if json_data["rdate"] == None else formattime(json_data["rdate"]))
            

    # Print commands
    print """---------------------------------
COMMANDS:

    Type 'users' to view USERS.
    Type 'reservations' to view RESERVATIONS.
    Type 'items' to view ITEMS.
    
    Type 'modify' to MODIFY reservation.
    Type 'delete' to DELETE reservation.
    
    Type 'quit' to QUIT.
"""

    # Selection prompt
    while True:
        
        selection = raw_input("Selection: ")

        if selection == "users":
            userspage()
        elif selection == "items":
            itemspage()
        elif selection == "reservations":
            reservationspage()

        elif selection == "modify":
            modify("reservation", href)
        elif selection == "delete":
            r = requests.delete(href)
            if r.status_code == 204:
                print "Reservation deletion successful."
            else:
                print "Reservation deletion not succesful, response: %s" % r.status_code
            reservationspage()
            
        elif selection == "quit":
            print "Quitting program."
            os._exit(0)
            
        else:
            pass

# USER'S RESERVATIONS
def userreservations(user):
    # HREF
    href = "http://localhost:5000/resys/api/users/%s/userreservations" % user

    # Get user information
    r = requests.get(href)
    json_data = json.loads(r.text)

    # Print user
    print "\n\nUSER RESERVATIONS FOR: %s\n%s\n---------------------------------\n" % (user, href)

    for entry in json_data["collection"]["items"]:
        r = requests.get("http://localhost:5000%s" % entry["href"])
        json_data = json.loads(r.text)

        r2 = requests.get("http://localhost:5000/resys/api/items/%s/" % json_data["item"])
        json_data2 = json.loads(r2.text)
        
        print """RESERVATION ID: %s
\nITEM NUMBER: %s
\nITEM NAME: %s
\nUSER: %s
\nLOAN DATE: %s
\nRETURN DATE: %s
""" % (json_data["reservation_ID"],
     json_data["item"],
     json_data2["name"],
     json_data["user"],
     formattime(json_data["ldate"]),
     "" if json_data["rdate"] == None else formattime(json_data["rdate"]))

        print "---------------------------------"

    # Print commands
    print """COMMANDS:

    Type 'users' to view USERS.
    Type 'reservations' to view RESERVATIONS.
    Type 'items' to view ITEMS.
    
    Type 'quit' to QUIT.
"""
    
    # Selection prompt
    while True:
        
        selection = raw_input("Selection: ")

        if selection == "users":
            userspage()
        elif selection == "items":
            itemspage()
        elif selection == "reservations":
            reservationspage()
            
        elif selection == "quit":
            print "Quitting program."
            os._exit(0)
            
        else:
            pass

# ITEM'S RESERVATIONS
def itemreservations(item):
    # HREF
    href = "http://localhost:5000/resys/api/items/%s/itemreservations" % item

    # Get item information
    r = requests.get(href)
    json_data = json.loads(r.text)

    # Print item
    print "\n\nITEM RESERVATIONS FOR: %s\n%s\n---------------------------------\n" % (item, href)

    for entry in json_data["collection"]["items"]:
        r = requests.get("http://localhost:5000%s" % entry["href"])
        json_data = json.loads(r.text)

        r2 = requests.get("http://localhost:5000/resys/api/items/%s/" % json_data["item"])
        json_data2 = json.loads(r2.text)
        
        print """RESERVATION ID: %s
\nITEM NUMBER: %s
\nITEM NAME: %s
\nUSER: %s
\nLOAN DATE: %s
\nRETURN DATE: %s
""" % (json_data["reservation_ID"],
     json_data["item"],
     json_data2["name"],
     json_data["user"],
     formattime(json_data["ldate"]),
     "" if json_data["rdate"] == None else formattime(json_data["rdate"]))

        print "---------------------------------"

    # Print commands
    print """COMMANDS:

    Type 'users' to view USERS.
    Type 'reservations' to view RESERVATIONS.
    Type 'items' to view ITEMS.
    
    Type 'quit' to QUIT.
"""
    
    # Selection prompt
    while True:
        
        selection = raw_input("Selection: ")

        if selection == "users":
            userspage()
        elif selection == "items":
            itemspage()
        elif selection == "reservations":
            reservationspage()
            
        elif selection == "quit":
            print "Quitting program."
            os._exit(0)
            
        else:
            pass



# ADD PROMPT
def add(selection):

    # ADD USER
    if selection == "user":
        
        # Ask for user information
        username = raw_input("Give username or type 'cancel' to cancel: ")
        if username.lower() == "cancel":
            userspage()
        elif username == "":
            username = None
            
        firstname = raw_input("Give first name or type 'cancel' to cancel: ")
        if firstname.lower() == "cancel":
            userspage()
        elif firstname == "":
            firstname == None

        lastname = raw_input("Give last name or type 'cancel' to cancel: ")
        if lastname.lower() == "cancel":
            userspage()
        elif lastname == "":
            firstname == None
            
        mobile = raw_input("Give mobile number or type 'cancel' to cancel: ")
        if mobile.lower() == "cancel":
            userspage()
        elif mobile == "":
            mobile == None
            
        email = raw_input("Give email address or type 'cancel' to cancel: ")
        if email.lower() == "cancel":
            userspage()
        elif email == "":
            email == None

        # Create user template
        usertoadd = {"template":{
            "data":[
                {"prompt":"","name":"useraccount","value":username},
                {"prompt":"","name":"firstname","value":firstname},
                {"prompt":"","name":"lastname","value":lastname},
                {"prompt":"","name":"email","value":email},
                {"prompt":"","name":"mobile","value":mobile}
                ]
            }
        }

        # POST call to server
        r = requests.post("http://localhost:5000/resys/api/users/",
                          data=json.dumps(usertoadd),
                          headers={"Accept":"application/json","Content-Type":"application/json"})

        if r.status_code == 201:
            print "Adding user..."
        elif r.status_code == 400:
            print "User addition failed."
            print "Malformed data, response: %s" % r.status_code
        elif r.status_code == 409:
            print "User addition failed."
            print "User already exists, response: %s" % r.status_code

        # Go back to users page
        userspage()
        
    # ADD ITEM
    elif selection == "item":
        itemname = None
        description = None
        status = None

        # Ask for item information
        itemname = raw_input("Give item name or type 'cancel' to cancel: ")
        if itemname.lower() == "cancel":
            itemspage()
        elif itemname == "":
            itemname = None

        description = raw_input("Give description or type 'cancel' to cancel: ")
        if description.lower() == "cancel":
            itemspage()
        elif description == "":
            description = None

        status = raw_input("Give status (0 or 1) or type 'cancel' to cancel: ")
        if status.lower() == "cancel":
            itemspage()
        elif status != "0" and status != "1":
            status = None

        itemtoadd = {"template":{
                "data":[
                    {"prompt":"","name":"name","value":itemname},
                    {"prompt":"","name":"description","value":description},
                    {"prompt":"","name":"status","value":status}
                    ]
                }
            }

        # POST call to server
        r = requests.post("http://localhost:5000/resys/api/items/",
                          data=json.dumps(itemtoadd),
                          headers={"Accept":"application/json","Content-Type":"application/json"})

        if r.status_code == 201:
            print "Adding item..."
        elif r.status_code == 400:
            print "Item addition failed."
            print "Malformed data, response: %s" % r.status_code
        elif r.status_code == 409:
            print "Item addition failed."
            print "Item already exists, response: %s" % r.status_code

        # Go back to items page
        itemspage()

    # ADD RESERVATION
    else:

        ldate = None
        rdate = None
        
        item = raw_input("Give item ID or type 'cancel' to cancel: ")
        if item == "cancel":
            reservationspage()
        elif item == "":
            item == "None"
        
        username = raw_input("Give username or type 'cancel' to cancel: ")
        if username == "cancel":
            reservationspage()
        elif username == "":
            username == "None"
            
        while ldate == None:
            ldate = raw_input("Give loan date (DD.MM.YYYY HH:MM) or type 'cancel' to cancel: ")
            if ldate == "cancel":
                reservationspage()
            elif inputtime(ldate) == None:
                ldate = None
                print "Date not given in proper format."
            else:
                ldate = inputtime(ldate)

        while rdate == None:
            rdate = raw_input("Give return date (DD.MM.YYYY HH:MM) or type 'cancel' to cancel: ")
            if rdate == "cancel":
                reservationspage()
            elif inputtime(rdate) == None:
                rdate = None
                print "Date not given in proper format."
            else:
                rdate = inputtime(rdate)
     
        reservationtoadd = {"template":
                            {"data":
                                [
                                {"prompt":"","name":"user","value":username},
                                {"prompt":"","name":"rdate","value":rdate},
                                {"prompt":"","name":"ldate","value":ldate},
                                {"prompt":"","name":"item","value":item},
                                ]
                            }
                        }
        
        # POST call to server
        r = requests.post("http://localhost:5000/resys/api/reservations/",
                  data=json.dumps(reservationtoadd),
                  headers={"Accept":"application/json","Content-Type":"application/json"})

        if r.status_code == 201:
            print "Adding reservation..."
        elif r.status_code == 400:
            print "Reservation addition failed."
            print "Malformed data, response: %s" % r.status_code
        elif r.status_code == 409:
            print "Reservation addition failed."
            print "Reservation already exists, response: %s" % r.status_code

        # Go back to reservations page
        reservationspage()



def modify(selection, href):
    
    # MODIFY USER
    if selection == "user":

        r = requests.get(href)
        json_data = json.loads(r.text)

        oldfn = json_data["firstname"]
        oldln = json_data["lastname"]
        oldmob = json_data["mobile"]
        oldem = json_data["email"]

        newfirstname = raw_input("Give new first name, type 'cancel' to cancel or press ENTER to keep username: ")
        if newfirstname == "cancel":
            userspage()
        elif newfirstname == "":
            newfirstname = oldfn
                
        newlastname = raw_input("Give new last name, type 'cancel' to cancel or press ENTER to keep last name: ")
        if newlastname == "cancel":
            userspage()
        elif newlastname == "":
            newlastname = oldln
  
        newmobile = raw_input("Give new mobile number, type 'cancel' to cancel or press ENTER to keep mobile number: ")
        if newmobile == "cancel":
            userspage()
        elif newmobile == "":
            newmobile = oldmob
            
        newemail = raw_input("Give new email address, type 'cancel' to cancel or press ENTER to keep email address: ")
        if newemail == "cancel":
            userspage()
        elif newemail == "":
            newemail = oldem
            
        # User to modify
        usertomodify = {"template":{
            "data":[
                {"prompt":"","name":"firstname","value":newfirstname},
                {"prompt":"","name":"lastname","value":newlastname},
                {"prompt":"","name":"email","value":newemail},
                {"prompt":"","name":"mobile","value":newmobile}
                ]
            }
        }

        # PUT call to server
        r = requests.put((href),
                         data=json.dumps(usertomodify),
                         headers={"Accept":"application/json","Content-Type":"application/json"})

        if r.status_code == 204:
            print "Modifying user..."
        elif r.status_code == 400:
            print "User modification failed."
            print "Malformed data, response: %s" % r.status_code

        # Go back to users page
        userspage()

    # MODIFY ITEM
    if selection == "item":

        r = requests.get(href)
        json_data = json.loads(r.text)

        oldname = json_data["name"]
        olddesc = json_data["description"]
        oldstat = json_data["status"]

        newname = raw_input("Give new item name, type 'cancel' to cancel or press ENTER to keep last name: ")
        if newname == "cancel":
            itemspage()
        elif newname == "":
            newname = oldname
  
        newdesc = raw_input("Give new description, type 'cancel' to cancel or press ENTER to keep mobile number: ")
        if newdesc == "cancel":
            itemspage()
        elif newdesc == "":
            newdesc = olddesc
            
        newstat = raw_input("Give new status, type 'cancel' to cancel or press ENTER to keep email address: ")
        if newstat == "cancel":
            itemspage()
        elif newstat != "0" and newstat != "1":
            newstat = oldstat
            
        # User to modify
        itemtomodify = {"template":{
                "data":[
                    {"prompt":"","name":"name","value":newname},
                    {"prompt":"","name":"description","value":newdesc},
                    {"prompt":"","name":"status","value":newstat}
                    ]
                }
            }

        # PUT call to server
        r = requests.put((href),
                         data=json.dumps(itemtomodify),
                         headers={"Accept":"application/json","Content-Type":"application/json"})

        if r.status_code == 204:
            print "Modifying item..."
        elif r.status_code == 400:
            print "Item modification failed."
            print "Malformed data, response: %s" % r.status_code

        # Go back to users page
        itemspage()

    # MODIFY RESERVATION
    if selection == "reservation":

        newldate = None
        newrdate = None
        
        r = requests.get(href)
        json_data = json.loads(r.text)

        olditem = json_data["item"]
        olduser = json_data["user"]
        oldldate = json_data["ldate"]
        oldrdate = json_data["rdate"]

        newitem = raw_input("Give new item ID, type 'cancel' to cancel or press ENTER to keep last name: ")
        if newitem == "cancel":
            reservationspage()
        elif newitem == "":
            newitem = olditem
  
        newuser = raw_input("Give new username, type 'cancel' to cancel or press ENTER to keep mobile number: ")
        if newuser == "cancel":
            reservationspage()
        elif newuser == "":
            newuser = olduser

        while newldate == None:
            newldate = raw_input("Give new loan date (DD.MM.YYYY HH:MM) or type 'cancel' to cancel: ")
            if newldate == "cancel":
                reservationspage()
            elif newldate == "":
                newldate = oldldate
            elif inputtime(newldate) == None:
                newldate = None
                print "Date not given in proper format."
            else:
                newldate = inputtime(newldate)

        while newrdate == None:
            newrdate = raw_input("Give new return date (DD.MM.YYYY HH:MM) or type 'cancel' to cancel: ")
            if newrdate == "cancel":
                reservationspage()
            elif newrdate == "":
                newrdate = oldrdate
            elif inputtime(newrdate) == None:
                newrdate = None
                print "Date not given in proper format."
            else:
                newrdate = inputtime(newrdate)

        # Reservation to modify
        reservationtomodify = {"template":
                            {"data":
                                [
                                {"prompt":"","name":"user","value":newuser},
                                {"prompt":"","name":"rdate","value":newrdate},
                                {"prompt":"","name":"ldate","value":newldate},
                                {"prompt":"","name":"item","value":newitem},
                                ]
                            }
                        }

        # PUT call to server
        r = requests.put((href),
                         data=json.dumps(reservationtomodify),
                         headers={"Accept":"application/json","Content-Type":"application/json"})

        if r.status_code == 204:
            print "Modifying reservation..."
        elif r.status_code == 400:
            print "Reservation modification failed."
            print "Malformed data, response: %s" % r.status_code

        # Go back to users page
        reservationspage()

        

# MAIN PROGRAM
def main():
    while True:
        try:
            userspage()

        # User interrupts, quit program
        except KeyboardInterrupt:
            print "Quitting program."
            os._exit(0)
            
        # No connection, quit program
        except requests.ConnectionError:
            print "No connection. Quitting program."
            os._exit(0)



# RUN MAIN PROGRAM
if __name__ == "__main__":
    main()
