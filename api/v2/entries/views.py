import datetime
import os,sys
sys.path.insert(0, os.path.abspath(".."))
import jwt
from functools import wraps

from flask import *
from models import *
from __init__ import *
from flask_restful import Api, Resource
from common import Common

apps = Blueprint("entries", __name__)
api = Api(apps)

connection = DatabaseModel.connection

class CreateEntry(Resource):
    #create an entry
    @Common.on_session
    def post(self):
        try:
            data = request.get_json()
            title = data['title']
            entry = data['entry']
        except KeyError:
            abort(422)
            return jsonify('provide title and entry to be saved')
        if title.strip() == '' or entry.strip() == '':
            return jsonify('title and entry cannot be empty')
        user_id = jwt.decode(request.args.get('token'), app.secret_key)['user_id']
        cursor = connection.cursor()
        sql = "insert into entries \
        (title,entry,id)values('"+title+"','"+entry+"','"+str(user_id)+"');"
        cursor.execute(sql)
        connection.commit()
        return jsonify("entry was successfully saved")
    
    #get all entries
    @Common.on_session
    def get(self):
        user_id = jwt.decode(request.args.get('token'), app.secret_key)['user_id']
        sql = "select * from entries where id = "+str(user_id)+";"
        cursor = connection.cursor()
        output = []
        cursor.execute(sql)
        result = cursor.fetchall()
        for each in result:
            output.append([str(each[0]),each[1],each[2],str(each[4])])
        connection.commit() 
        return jsonify(output)
    
    
class EntryId(Resource):
                
     #modify an entry      
    @Common.on_session
    def put(self, entry_id):
        try:
            user_id = jwt.decode(request.args.get('token'), app.secret_key)['user_id']
            title = request.get_json()['title']
            entry = request.get_json()['entry']
        except KeyError:
            return jsonify('provide new title and new entry to replace')            
        if title.strip() == '' or entry.strip() == '':
            return jsonify('title and entry cannot be empty')
        today = str(datetime.datetime.today()).split()
        if Common().authorize(request.args.get('token')):
            cursor = connection.cursor()
            sqlcheck = "select * from entries where entryid="+str(entry_id)+";"
            cursor.execute(sqlcheck)
            result = cursor.fetchone()
            if result[3] != user_id:
                return jsonify("you are not the author of this entry")
            elif str(result[4]).split()[0] != today[0]:
                return jsonify("you can only modify an entry created today")
            sql = "UPDATE entries SET title=\
            '"+title+"',entry='"+entry+"'where entryID="+str(entry_id)+";"
            cursor.execute(sql)
            connection.commit()
            return jsonify("succesfully edited")
        return jsonify("you are out of session")
     
     #delete an entry
    @Common.on_session           
    def delete(self, entry_id):
        user_id = jwt.decode(request.args.get('token'), app.secret_key)['user_id']
        cursor = connection.cursor()
        sql1 = "select * from entries where entryid = "+str(entry_id)+";"
        sql = "delete from entries \
        where entryid = "+str(entry_id)+" and id = "+str(user_id)+";"
        cursor.execute(sql1)
        result = cursor.fetchone()
        if result is None:
            return jsonify("the entry has already been deleted")
        elif result[3] != user_id:
            return jsonify("you are not authorized to perform the operation")
        cursor.execute(sql)
        connection.commit()
        return jsonify("delete successful")
    
    #get one entry
    @Common.on_session
    def get(self, entry_id):
        user_id = jwt.decode(request.args.get('token'), app.secret_key)['user_id']
        sql = "select * from entries \
        where entryid = "+str(entry_id)+" and id = "+str(user_id)+";"
        cursor = connection.cursor()
        cursor.execute(sql)
        result = cursor.fetchone()
        if result is None:
            abort(401)
            return jsonify("entry id "+str(entry_id)+" is \
            not part of your entries . you can only view your entries")
        connection.commit()
        return  jsonify(result[0],result[1],result[2],result[4])        

api.add_resource(CreateEntry, '/api/v2/entries')
api.add_resource(EntryId, '/api/v2/entries/<int:entry_id>')