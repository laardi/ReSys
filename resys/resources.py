'''
resources.py
Written by Lauri
Some code borrowed from Ivan
Last edited: 1.9.15
'''
import json

from flask import Flask, request, Response, g, jsonify
from flask.ext.restful import Resource, Api, abort
from werkzeug.exceptions import NotFound, UnsupportedMediaType

from utils import RegexConverter
import database

#

DEFAULT_DB_PATH = 'db/resys.db'
# Constants for profiles and stuff
USER_PROFILE = "link to user profile"
ITEM_PROFILE = "link to item profile"
RESERVATION_PROFILE = "link to reservation profile"
COLLECTIONJSON = "application/vnd.collection+json"
HAL = "application/hal+json"

#Application and api
app = Flask(__name__)
app.debug = True
app.config.update({'DATABASE':database.ResysDatabase(DEFAULT_DB_PATH)})

api = Api(app)

def create_error_response(status_code, title, message, resource_type=None):
    response = jsonify(title=title, message=message, resource_type=resource_type)
    response.status_code = status_code
    return response

@app.errorhandler(404)
def resource_not_found(error):
    return create_error_response(404, "Resource not found", "This resource url does not exit")

@app.errorhandler(500)
def unknown_error(error):
    return create_error_response(500, "Error", "The system has failed. Please, contact the administrator")


@app.before_request
def set_database():
    '''
    Stores an instance of the database API before each request in the flask.g
    variable, accessable only from the application context
    '''

    g.db = app.config['DATABASE']


#Define the resources
class Users(Resource):
    '''
    Resource Users implementation
    '''

    def get(self):
        '''
        Gets a list of all users in the system

        INPUT:
            None
        OUTPUT:
            {"collection":{
                "version":"1.0",
                "href":"resys/api/users/",
                "links":[{"prompt":"List of all items in the system",
                            "rel": "items-all",
                            "href":"resys/api/items/"
                    },
                "template":{
                      "data" : [
                        {"prompt" : "Insert nickname", "name" : "useraccount",
                         "value" : "", "required":True},
                        {"prompt" : "Insert user email", "name" : "email",
                         "value" : "", "required":True},
                        {"prompt" : "Insert user lastname", "name" : "lastname",
                         "value" : "", "required":True},
                        {"prompt" : "Insert user firstname", "name" : "firstname",
                         "value" : "", "required":True},
                        {"prompt" : "Insert user mobile", "name" : "mobile",
                         "value" : "", "required":False}
                      ]
                    },
                "items":{[
                        {"data":[{
                                "name":"useraccount",
                                "value":"sampooko"
                            }],
                            "href":"/resys/api/users/sampooko/",
                            "read-only": True

                        },
                        {"data":[{
                                "name":"useraccount",
                                "value":"jorge"
                            }],
                            "href":"/resys/api/users/jorge/",
                            "read-only": True
                        }
                    ]}    
                }
            }
        '''


        users_db = g.db.GetUsers()

        envelope = {}
        collection = {}
        envelope["collection"] = collection
        collection['version'] = "1.0"
        collection['href'] = api.url_for(Users)
        collection['links'] = [{'prompt':'List of all items in the system', 
                              'rel':'items-all',
                              'href': api.url_for(Items)}
                            ]
        collection['template'] = {
          "data" : [
            {"prompt" : "Insert nickname", "name" : "useraccount",
             "value" : "", "required":True},
            {"prompt" : "Insert user email", "name" : "email",
             "value" : "", "required":True},
            {"prompt" : "Insert user lastname", "name" : "lastname",
             "value" : "", "required":True},
            {"prompt" : "Insert user firstname", "name" : "firstname",
             "value" : "", "required":True},
            {"prompt" : "Insert user mobile", "name" : "mobile",
             "value" : "", "required":False}
          ]
        }
        #Create the items
        items = []
        for user in users_db: 
            _nickname = user['useraccount']
            _url = api.url_for(User, useraccount=_nickname)
            user = {}
            user['href'] = _url
            user['read-only'] = True
            user['data'] = []
            value = {'name':'useraccount', 'value':_nickname}
            user['data'].append(value)
            items.append(user)
        collection['items'] = items
        #RENDER

        return envelope


    def post(self):
        '''
        INPUT: 
        {"template":{
            "data":[
                {"prompt":"","name":"useraccount","value":""},
                {"prompt":"","name":"email","value":""},
                {"prompt":"","name":"lastname","value":""},
                {"prompt":"","name":"firstname","value":""}
                ]
            }
        }

        Adds a new user to database
        '''
        #PARSE THE REQUEST:
        inputa = request.get_json(force=True)
        if not inputa:
            return create_error_response(415, "Unsupported Media Type",
                                         "Use a JSON compatible format",
                                         "User")
        #Get the request body and serialize it to object 
        #We should check that the format of the request body is correct. Check
        #That mandatory attributes are there.
    
        data = inputa['template']['data']
        _useraccount = None
        _email = None
        _lastname = None
        _firstname = None
        _mobile = None
        for d in data:
        #This code has a bad performance. We write it like this for
        #simplicity. Another alternative should be used instead. E.g. 
        #generation expressions
            if d['name'] == "email":
                _email = d['value']
            elif d['name'] == "lastname":
                _lastname = d['value']
            elif d['name'] == "firstname":
                _firstname = d['value']
            elif d['name'] == "mobile":
                _mobile = d['value']
            elif d['name'] == "useraccount":
                _useraccount = d['value']
        #Error if not required value
        if not _email or not _lastname or \
        not _firstname or not _useraccount:
            return create_error_response(400, "Wrong request format",
                                              "Be sure you include all mandatory"\
                                              "properties",
                                              "User") 
        #Conflict if user already exist
        if g.db.ContainsUser(_useraccount):
            return create_error_response(409, "Wrong useraccount",
                                              "There is already a user with same useraccount %s.\
                                               Try another one " % _useraccount,
                                              "User")

        user =  {'useraccount': _useraccount,
                'firstname':_firstname,
                'lastname':_lastname,
                'email':_email,
                'mobile':_mobile,
                }
        

        #But we are not going to do this exercise
        uid = g.db.AddUser(user)
        #CREATE RESPONSE AND RENDER
        return  Response(status=201, 
                         headers={"Location":api.url_for(User, 
                            useraccount=g.db.GetUserAccount(uid))}
                        )



class User(Resource):
    '''
    User resource stuff
    '''

    def get(self, useraccount):
        
        user_db = g.db.GetUser(useraccount)
        if not user_db:
            return create_error_response(404,"Unknown user",
            "There is no user with account %s" % useraccount,"User")

        #Filter and generateresponse
        #Create envelope
        envelope = {}
        links = {}
        envelope['_links'] = links

        #Fill the links
        links['self'] = {'href':api.url_for(User, useraccount=useraccount),
                         'profile': USER_PROFILE,
                         'type':COLLECTIONJSON}
        links['collection'] = {'href':api.url_for(Users),
                               'profile': USER_PROFILE,
                               'type':COLLECTIONJSON}
        links['reservations'] = {
                            'href':api.url_for(UserReservations, user_id=useraccount),
                            'profile': RESERVATION_PROFILE,
                            'type':COLLECTIONJSON}
        #links['data'] = {
        #                    'href':api.url_for(User, useraccount=useraccount),
        #                    'profile': USER_PROFILE,
        #                    'type':COLLECTIONJSON}

        envelope['useraccount'] = useraccount
        envelope['email'] = user_db['email']
        envelope['firstname'] = user_db['firstname']
        envelope['lastname'] = user_db['lastname']
        envelope['mobile'] = user_db['mobile']
        
        envelope['template'] = {"data": [
                                    {"prompt": "Insert useraccount",
                                     "name":"useraccount",
                                     "value": "",
                                     "required":True},
                                    {"prompt": "Insert email",
                                     "name":"email",
                                     "value": "",
                                     "required":True},
                                    {"prompt": "Insert firstname",
                                     "name":"firstname",
                                     "value": "",
                                     "required":True},
                                    {"prompt": "Insert lastname",
                                     "name":"lastname",
                                     "value": "",
                                     "required":True},
                                    {"prompt": "Insert mobile",
                                     "name":"mobile",
                                     "value": "",
                                     "required":False}
                                    ]
                                }

        return Response(json.dumps(envelope),200, mimetype=HAL+";"+USER_PROFILE)

    def put(self, useraccount):
        '''
        Updates the user stuff
        '''
        if g.db.ContainsUser(useraccount):
            input = request.get_json(force=True)
            if not input:
                raise create_error_response(415, "Unsupported Media Type",
                                        "Use a JSON compatible format",
                                        "User")
            try:

                user_data = input['template']['data']

                _email = None
                _lastname = None
                _firstname = None
                _mobile = None
                for d in user_data:
                #This code has a bad performance. We write it like this for
                #simplicity. Another alternative should be used instead. E.g. 
                #generation expressions
                    if d['name'] == "email":
                        _email = d['value']
                    elif d['name'] == "lastname":
                        _lastname = d['value']
                    elif d['name'] == "firstname":
                        _firstname = d['value']
                    elif d['name'] == "mobile":
                        _mobile = d['value']
                if not _email or not _lastname or not _firstname or not _mobile:
                    return create_error_response(400, "Wrong request format",
                                        "Be suressd you include all needed values",
                                        "User")
            except:
                return create_error_response(400, "Wrong request format",
                            "Be sure you include all needed values",
                            "User")
                
            user = {'firstname':_firstname,
                    'lastname':_lastname,
                    'email':_email,
                    'mobile':_mobile
                    }
            useraccount = g.db.ModifyUser(useraccount, user)
            
            #return Response(status=204,
            #                headers={"Location":api.url_for(User,
            #                                useraccount=useraccount)
            #                        }
            #                )
            return '', 204
        else:
            abort(404)

    def delete(self, useraccount):
        '''
        Deletes the user from database
        '''
        #PEROFRM OPERATIONS
        #Try to delete the user. If it could not be deleted, the database
        #returns None.
        u_id = g.db.GetUserID(useraccount)
        if g.db.DeleteUser(u_id) is None:
            #RENDER RESPONSE
            return '', 204
        else:
            #GENERATE ERROR RESPONSE
            abort(404,  message="There is no a user with useraccount %s" 
                                 % useraccount, 
                        resource_type="User", 
                        resource_url=request.path, 
                        resource_id=useraccount)

class Item(Resource):
    '''
    Item resource implementation
    '''

    def get(self, id):
        '''
        Retrieves the information of an item with certain ID
        '''
        item = g.db.GetItem(id)
        if not item:
            abort(404, message="There is no item with id %s" % id,
                        resource_type="Item",
                        resource_url=request.path,
                        resource_id=id)
        envelope = {}
        links = {}
        envelope['_links'] = links

        #Fill the links
        links['self'] = {'href':api.url_for(Item, id=id),
                         'profile': ITEM_PROFILE}
        links['collection'] = {'href':api.url_for(Items),
                               'profile': ITEM_PROFILE,
                               'type':COLLECTIONJSON}
        links['reservations'] = {
                            'href':api.url_for(ItemReservations, id=id),
                            'profile': RESERVATION_PROFILE,
                            'type':COLLECTIONJSON}
        #links['data'] = {
        #                    'href':api.url_for(Item, id=id),
        #                    'profile': ITEM_PROFILE,
        #                    'type':COLLECTIONJSON}

        envelope['itemID'] = id
        envelope['name'] = item['name']
        envelope['description'] = item['description']
        envelope['status'] = item['status']
        
        envelope['template'] = {"data": [
                                    {"prompt": "Insert item name",
                                     "value": "",
                                     "required":True},
                                    {"prompt": "Insert description",
                                     "value": "",
                                     "required":True},
                                    {"prompt": "Insert status",
                                     "value": "",
                                     "required":False}
                                    ]
                                }
        return envelope

    def put(self, id):
        ''' 
        Updates item properties
        Takes in JSON
        {
            "name:"",
            "status":"",
            "description":""
        }
        '''
        if g.db.GetItem(id):
            input = request.get_json(force=True)
            if not input:
                raise create_error_response(415, "Unsupported Media Type",
                                        "Use a JSON compatible format",
                                        "Item")
            """
            if not all(attr in item_data for attr in\
                ('name','status','description')):
                abort(400)
            item = {}  
            item['name'] = item_data['name']
            item['status'] = item_data['status']
            item['description'] = item_data['description']
            g.db.ModifyItem(id, item)
            
            return Response(status=204,
                            headers={"Location":api.url_for(Item,
                                            id=id)
                                     })"""
            try:

                item_data = input['template']['data']


                _name = None
                _description = None
                _status = None
                for d in item_data:
                #This code has a bad performance. We write it like this for
                #simplicity. Another alternative should be used instead. E.g. 
                #generation expressions
                    if d['name'] == "name":
                        _name = d['value']
                    elif d['name'] == "description":
                        _description = d['value']
                    elif d['name'] == "status":
                        _status = d['value']

                if not _name or not _description or not _status:
                    return create_error_response(400, "Wrong request format",
                                        "Be suressd you include all needed values",
                                        "Item")
            except:
                return create_error_response(400, "Wrong request format",
                            "Bdasdae sure you include all needed values",
                            "Item")
                
            item = {'name':_name,
                    'description':_description,
                    'status':_status
                    }
            itemid = g.db.ModifyItem(id, item)
            
            #return Response(status=204,
            #                headers={"Location":api.url_for(User,
            #                                useraccount=useraccount)
            #                        }
            #                )
            return '', 204
                            
        else:
            abort(404)
    
    def delete(self, id):
        #PEROFRM OPERATIONS
        #Try to delete the item. If it could not be deleted, the database
        #returns None.

        
        if g.db.DeleteItem(id) is None:
            #RENDER RESPONSE
            return Response(status=204)
        else:
            #GENERATE ERROR RESPONSE
            abort(404,  message="There is no a item with id %s" 
                                 % id, 
                        resource_type="Item", 
                        resource_url=request.path, 
                        resource_id=id)


class Items(Resource):
    '''
    Item resource implementation
    '''

    def get(self):
        '''
        Gets a list of all items in the system

        INPUT:
            None
        OUTPUT:
            [{'items':{'id':.....},....]
        
        '''
        #Extract items from the database
        items_db = g.db.GetItems()

        #FILTER AND GENERATE RESPONSE

        #Create the envelope
        envelope = {}
        collection = {}
        envelope["collection"] = collection
        collection['version'] = "1.0"
        collection['href'] = api.url_for(Items)
        collection['links'] = [{'prompt':'List of all users in the Forum', 
                              'rel':'users-all','href': api.url_for(Users)}
                            ]
        collection['template'] = {
          "data" : [
            {"prompt" : "", "name" : "name", "value" : "", "required":True},
            {"prompt" : "", "name" : "description", "value" : "", "required":True},
            {"prompt" : "", "name" : "status", "value" : "", "required":True}
          ]
        }
        #Create the items
        items = []
        for item in items_db: 
            _itemid = item['id']
            _name = item['name']
            _url = api.url_for(Item, id=_itemid)
            item = {}
            item['href'] = _url
            item['data'] = []
            value = {'name':'name', 'value':_name}
            item['data'].append(value)
            value = {'name':'id', 'value':_itemid}
            item['data'].append(value)
            item['read-only'] = True

            items.append(item)
        collection['items'] = items
        
        #RENDER
        return envelope

    def post(self):
        '''
        Post a new item into the database

        Takes in JSON:
            {"template":{
                "data":[
                    {"prompt":"","name":"name","value":""},
                    {"prompt":"","name":"description","value":""},
                    {"prompt":"","name":"satus","value":""}
                    ]
                }
            }
        '''

        #PARSE THE REQUEST:
        inputa = request.get_json(force=True)
        if not inputa:
            return create_error_response(415, "Unsupported Media Type",
                                         "Use a JSON compatible format",
                                         "Item")
        #Get the request body and serialize it to object 
        #We should check that the format of the request body is correct. Check
        #That mandatory attributes are there.
    
        data = inputa['template']['data']
        _name = None
        _description = None
        _status = None
        for d in data:
        #This code has a bad performance. We write it like this for
        #simplicity. Another alternative should be used instead. E.g. 
        #generation expressions
            if d['name'] == "name":
                _name = d['value']
            elif d['name'] == "description":
                _description = d['value']
            elif d['name'] == "status":
                _status = d['value']
        #Error if not required value
        if not _name or not _description or not _status:
            return create_error_response(400, "Wrong request format",
                                              "Be sure you include all mandatory"\
                                              "properties",
                                              "Item") 
        #Conflict if user already exist
        if g.db.HoldsItem(_name):
            return create_error_response(409, "Wrong item name",
                                              "There is already an item with name %s.\
                                               Try another one " % _name,
                                              "Item")

        item =  {'name': _name,
                'status':_status,
                'description':_description
                }
        

        #But we are not going to do this exercise
        iid = g.db.AddItem(item)
        #CREATE RESPONSE AND RENDER
        return  Response(status=201, 
                         headers={"Location":api.url_for(Item, 
                            id=iid)}
                        )


class Reservation(Resource):
    '''
    Reseravariotn!
    '''

    def get(self, id):
        reservation = g.db.GetReservation(id)
        
        if not reservation:
            abort(404, message="There is no reservation with id %s" % id,
                        resource_type="Reservation",
                        resource_url=request.path,
                        resource_id=id)
        #Filter and generateresponse
        envelope = {}
        links = {}
        envelope['_links'] = links

        links['self'] = {'href':api.url_for(Reservation, id=id),
                         'profile': RESERVATION_PROFILE,
                         'type':HAL}
        links['collection'] = {'href':api.url_for(Reservations),
                               'profile': RESERVATION_PROFILE,
                               'type':COLLECTIONJSON}
        links['items'] = {
                            'href':api.url_for(Items),
                            'profile': ITEM_PROFILE,
                            'type':COLLECTIONJSON}
        links['users'] = {'href':api.url_for(Users),
                               'profile': USER_PROFILE,
                               'type':COLLECTIONJSON}
        #links['data'] = {
        #                    'href':api.url_for(User, useraccount=useraccount),
        #                    'profile': USER_PROFILE,
        #                    'type':COLLECTIONJSON}

        envelope['user'] = g.db.GetUserAccount(reservation['user'])
        envelope['item'] = reservation['item']
        envelope['reservation_ID'] = reservation['id']
        envelope['rdate'] = reservation['rdate']
        envelope['ldate'] = reservation['ldate']

        envelope['template'] = {"data": [
                {"prompt":"Insert useraccount",
                 "name":"user",
                 "value":"",
                 "required":True},
                {"prompt":"Insert item id",
                 "name":"item",
                 "value":"",
                 "required":True},
                {"prompt":"Insert loan date",
                 "name":"ldate",
                 "value":"",
                 "required":True},
                {"prompt":"insert return date",
                 "name":"rdate",
                 "value":"",
                 "required":False}
                    ]
                }

        return Response(json.dumps(envelope),200, mimetype=HAL+";"+RESERVATION_PROFILE)

    def put(self, id):
        """
        INPUT:
        {"template":{
            "data":[
                    {"prompt":"","name":"item","value":""},
                    {"prompt":"","name":"user","value":""},
                    {"prompt":"","name":"ldate","value":""},
                    {"prompt":"","name":"rdate","value":""},
                    ]
                }
            }
        }

        """
        if g.db.GetReservation(id):
            r_data = request.get_json(force=True)
            if not r_data:
                raise create_error_response(415, "Unsupported Media Type",
                                        "Use a JSON compatible format",
                                        "Item")
            r_data = r_data["template"]["data"]
            _rdate = None
            _ldate = None
            _user = None
            _item = None
            for d in r_data:
                if d['name'] == "item":
                    _item = d['value']
                elif d['name'] == "user":
                    _user = d['value']
                elif d['name'] == "ldate":
                    _ldate = d['value']
                elif d['name'] == "rdate":
                    _rdate = d['value']
            if not _item or not _user or not _ldate:
                return create_error_response(400, "Wrong request format",
                                    "Be sure you include all needed values",
                                    "Reservation")
            reservation = {}  
            
            #Test if both item and user are valid
            if g.db.GetItem(_item) is None:
                abort(409,
                        Message="There is no item with following id: %s"%r_data['item'])
            if g.db.GetUserID(_user) is None:
                abort(409,
                        Message="There is no user with following name: %s"%r_data['user'])
            
            reservation['id'] = id
            reservation['item'] = _item
            reservation['user'] = g.db.GetUserID(_user)
            reservation['ldate'] = _ldate
            reservation['rdate'] = _rdate
            reservation_id = g.db.ModifyReservation(reservation)
            
            return Response(status=204,
                            headers={"Location":api.url_for(Reservation,
                                            id=reservation_id)
                                    }
                            )
        else:
            abort(404)




    def delete(self,id):

        if g.db.DeleteReservation(id):
            #RENDER RESPONSE
            return Response(status=204)
        else:
            #GENERATE ERROR RESPONSE
            abort(404,  message="There is no reservation with id %s" 
                                 % id, 
                        resource_type="Reservation", 
                        resource_url=request.path, 
                        resource_id=id)
        pass

class Reservations(Resource):
    '''
    OH YEAH
    '''

    def get(self):

        reservation_db = g.db.GetReservations()

        envelope = {}
        collection = {}
        envelope["collection"] = collection
        collection['version'] = "1.0"
        collection['href'] = api.url_for(Reservations)
        collection['links'] = [{'prompt':'List of all items in the system', 
                              'rel':'items-all',
                              'href': api.url_for(Items)},
                              {'prompt':'List of all users in the system', 
                              'rel':'users-all',
                              'href': api.url_for(Users)}
                            ]
        collection['template'] = {
          "data" : [
            {"prompt" : "Insert useraccount", "name" : "useraccount",
             "value" : "", "required":True},
            {"prompt" : "Insert item ID", "name" : "item",
             "value" : "", "required":True},
            {"prompt" : "Insert time of loan", "name" : "ldate",
             "value" : "", "required":True},
            {"prompt" : "Insert time of return", "name" : "rdate",
             "value" : "", "required":False}
          ]
        }
        #Create the items
        items = []
        for reservation1 in reservation_db: 
            _id = reservation1['id']
            _url = api.url_for(Reservation, id=_id)
            reservation = {}
            reservation['href'] = _url
            reservation['read-only'] = True
            reservation['data'] = []
            value = {'name':'reservation ID', 'value':_id}
            reservation['data'].append(value)
            value = {'name':'Item', 'value':reservation1['item']}
            reservation['data'].append(value)
            value = {'name':'User', 'value':reservation1['user']}
            reservation['data'].append(value)
            value = {'name':'Loandate', 'value':reservation1['ldate']}
            reservation['data'].append(value)
            value = {'name':'Returndate', 'value':reservation1['rdate']}
            reservation['data'].append(value)
            items.append(reservation)
        collection['items'] = items
        return envelope


    def post(self):
        '''
        INPUT 
        {"template":
            {"data":
                [
                {"prompt":"","name":"user","value":""},
                {"prompt":"","name":"rdate","value":""},
                {"prompt":"","name":"ldate","value":""},
                {"prompt":"","name":"item","value":""},
                ]
            }
        }
        '''
        reservation = request.get_json(force=True)
        if not reservation:
            raise create_error_response(415, "Unsupported Media Type",
                                    "Use a JSON compatible format",
                                    "Item")

        data = reservation["template"]["data"]

        _user = None
        _item = None
        _rdate = None
        _ldate= None

        for d in data:
            if d["name"] == "user":
                _user = d["value"]
            if d["name"] == "item":
                _item = d["value"]
            if d["name"] == "ldate":
                _ldate = d["value"]
            if d["name"] == "rdate":
                _rdate = d["value"]
        
        if not _user or not _item or not _ldate:
            return create_error_response(400, "Wrong request format",
                                              "Be sure you include all mandatory"\
                                              "properties",
                                              "Reservation") 
        #Check that both user and item are valid
        if g.db.GetItem(_item) is None:
            abort(409,
                    Message="There is no item with following id: %s"%_item)
        if g.db.GetUserID(_user) is None:
            abort(409,
                    Message="There is no user with following name: %s"%_user)
            
        reservation = {"user":_user,
                        "item":_item,
                        "ldate":_ldate,
                        "rdate":_rdate}

        reserv_id = g.db.AddReservation(reservation)

        #Create response and render
        return Response(status=201,
                        headers={"Location":api.url_for(Reservation,
                                                    id=reserv_id)}
                        )


class UserReservations(Resource):
    
    def get(self,user_id):
        '''
        user = useraccount
        '''
        _user_id = g.db.GetUserID(user_id)
        if _user_id is None:
            return abort(404)
        #9,Message="There is no user with name %s"%user_id)
        reservation_db = g.db.GetActiveReservations(_user_id)


        envelope = {}
        collection = {}
        envelope["collection"] = collection
        collection['version'] = "1.0"
        collection['href'] = api.url_for(Reservations)
        collection['links'] = [{'prompt':'List of all reservations in the system', 
                              'rel':'Reservations-all',
                              'href': api.url_for(Reservations)}
                            ]
        collection['template'] = {
          "data" : [
            {"prompt" : "Insert useraccount", "name" : "useraccount",
             "value" : "", "required":True},
            {"prompt" : "Insert item ID", "name" : "item",
             "value" : "", "required":True},
            {"prompt" : "Insert time of loan", "name" : "ldate",
             "value" : "", "required":True},
            {"prompt" : "Insert time of return", "name" : "rdate",
             "value" : "", "required":False}
          ]
        }
        #Create the items
        items = []
        for reservation1 in reservation_db: 
            _id = reservation1['id']
            _url = api.url_for(Reservation, id=_id)
            _r_user = reservation1['user']

            reservation = {}
            reservation['href'] = _url
            reservation['read-only'] = True
            reservation['data'] = []
            value = {'name':'reservation ID', 'value':_id}
            reservation['data'].append(value)
            value = {'name':'Item', 'value':reservation1['item']}
            reservation['data'].append(value)
            value = {'name':'User', 'value':g.db.GetUserAccount(_r_user)}
            reservation['data'].append(value)
            value = {'name':'Loandate', 'value':reservation1['ldate']}
            reservation['data'].append(value)
            value = {'name':'Returndate', 'value':reservation1['rdate']}
            reservation['data'].append(value)
            items.append(reservation)
        collection['items'] = items
        return envelope


class ItemReservations(Resource):
    
    def get(self, id):






        reservation_db = g.db.GetItemReservations(id)
        if reservation_db is None:
            return create_error_response(404,"Unknown item",
            "There is no item with id %s" % id,"Item")

        envelope = {}
        collection = {}
        envelope["collection"] = collection
        collection['version'] = "1.0"
        collection['href'] = api.url_for(Reservations)
        collection['links'] = [{'prompt':'List of all reservations in the system', 
                              'rel':'Reservations-all',
                              'href': api.url_for(Reservations)}
                            ]
        collection['template'] = {
          "data" : [
            {"prompt" : "Insert useraccount", "name" : "useraccount",
             "value" : "", "required":True},
            {"prompt" : "Insert item ID", "name" : "item",
             "value" : "", "required":True},
            {"prompt" : "Insert time of loan", "name" : "ldate",
             "value" : "", "required":True},
            {"prompt" : "Insert time of return", "name" : "rdate",
             "value" : "", "required":False}
          ]
        }
        #Create the items
        items = []
        for reservation1 in reservation_db: 
            _id = reservation1['id']
            _url = api.url_for(Reservation, id=_id)
            _r_user = reservation1['user']

            reservation = {}
            reservation['href'] = _url
            reservation['read-only'] = True
            reservation['data'] = []
            value = {'name':'reservation ID', 'value':_id}
            reservation['data'].append(value)
            value = {'name':'Item', 'value':reservation1['item']}
            reservation['data'].append(value)
            value = {'name':'User', 'value':g.db.GetUserAccount(_r_user)}
            reservation['data'].append(value)
            value = {'name':'Loandate', 'value':reservation1['ldate']}
            reservation['data'].append(value)
            value = {'name':'Returndate', 'value':reservation1['rdate']}
            reservation['data'].append(value)
            items.append(reservation)
        collection['items'] = items
        return envelope


#Regex converter for route defining
app.url_map.converters['regex'] = RegexConverter

#Routes
api.add_resource(Users,'/resys/api/users/',
                endpoint='users')
api.add_resource(User,'/resys/api/users/<useraccount>/',
                endpoint='user') 

api.add_resource(UserReservations,
                '/resys/api/users/<user_id>/userreservations/',
                endpoint='userreservations')

api.add_resource(Items,'/resys/api/items/',
                endpoint='items')
api.add_resource(Item,'/resys/api/items/<id>/',
                endpoint='item')
api.add_resource(ItemReservations,'/resys/api/items/<id>/itemreservations/',
                endpoint='itemreservations')

api.add_resource(Reservations,'/resys/api/reservations/',
                endpoint='reservations')
api.add_resource(Reservation,'/resys/api/reservations/<id>/',
                endpoint='reservation')



#Start ze app

if __name__ == '__main__':
    app.run(debug=True)

