## This script contains the server code. As a view, it can be replaced with another view
## Maintains /createproject and /requestproject

import string
import json
from time import strftime
from datetime import datetime       
from flask import request, jsonify
from sqlalchemy import func
from app import fapp , models

## Index page is kept to quickly test if server is up.
@fapp.route('/')
def index():
    return "Heya!" , 200

## createproject function as 
@fapp.route('/createproject', methods = ['POST'])
def createproject():
    ## Are we dealing with a JSON object?
    if request.get_json() != None:
        ## Get JSON Object fields
        jsonData = dict(request.get_json())
        try:
            ## These statements ensure that these fields are in the JSON object.
            ## If not, an exception is raised, caught, and handled
            iid = jsonData["id"]
            iprojectName = jsonData["projectName"]
            icreationDate = datetime.strptime(jsonData["creationDate"],"%m%d%Y %H:%M:%S")
            iexpiryDate = datetime.strptime(jsonData["expiryDate"],"%m%d%Y %H:%M:%S")
            ienabled = jsonData["enabled"]
            itargetCountries = jsonData["targetCountries"]
            iprojectCost = jsonData["projectCost"]
            itargetKeys = jsonData["targetKeys"]

            try:
                iprojectUrl = jsonData["projectUrl"]
            except :
                iprojectUrl = None

            ## Create ORM relationships, add objects to their specific tables.
            ## Note : Nothing is committed unless everything is accepted into the database.
            cIndex = 0

            ## Walk through each country in the json object list. Add it to the countries table
            ## Foreign key constraints are hooked up here as well.
            for country in itargetCountries:
                c = models.Country(tcid = iid, country = jsonData["targetCountries"][cIndex])
                cIndex+=1
                models.db.session.add(c)

            kIndex = 0
            for key in itargetKeys:
                k = models.Key(kid = iid, number = jsonData["targetKeys"][kIndex]["number"],
                                          keyword = jsonData["targetKeys"][kIndex]["keyword"])
                kIndex+=1
                models.db.session.add(k)

            project = models.Project(id = iid, projectName = iprojectName, creationDate = icreationDate,
                                      expiryDate = iexpiryDate, enabled = ienabled, targetCountries = iid,
                                      projectCost = iprojectCost, projectUrl = iprojectUrl, targetKeys = iid)
            
            models.db.session.add(project)
            models.db.session.commit()
            
            ## Added project to database, now write it to Projects.txt
            writeToProjects()
            
            return responseCode("Successfully Wrote To Projects") , 200
        except :

            ## If anything went wrong (missing fields for project)
            ## we don't commit our changes and return a Bad Request
            return responseCode("Unable to add project to database") , 400
    else:
        return responseCode("Not a Json Request") , 400

@fapp.route('/requestproject', methods = ['GET'])
def requestproject():

    ## Configure URL arguments. Allows for optional querying.
    projectid = request.args.get('projectid', default=None, type=int)
    country = request.args.get('country', default=None, type=str)
    number = request.args.get('number', default=None, type=int)
    keyword = request.args.get('keyword', default=None, type=str)

    try:
        ## CASE 1 :
        ## If a projectid was specified, we ignore the other rules and attempt to return
        ## a project with a matching id.
        if projectid != None:
           query = models.Project.query.filter_by(id = projectid)

           ## Did the executed query produce results?
           if query.count() != 0:

               ## Prepare information to send back to user.
               message = { "projectName" : query[0].projectName,
                           "projectCost" : query[0].projectCost,
                           "projectUrl"  : query[0].projectUrl }

               ## Send information back with OK (200) status code.
               return jsonify(message) , 200
           else:
               return responseCode("no project found") , 200

        ## CASE 2 :
        ## If no arguments were supplied, we look for the most expensive *valid project
        elif projectid == None and country == None and number == None and keyword == None:
           query = models.Project.query.filter(models.Project.expiryDate > func.now(), \
                                              models.Project.enabled == True, \
                                              models.Project.projectUrl != None). \
                                              order_by(models.Project.projectCost.desc())
           if query.count() != 0:
               message = { "projectName" : query[0].projectName,
                           "projectCost" : query[0].projectCost,
                           "projectUrl"  : query[0].projectUrl }
               return jsonify(message), 200
           else:
               return responseCode("no project found") , 200

        ## CASE 3 :
        ## Arguments were supplied. Filter accordingly with AND rules.
        else:

        ## Join all 3 tables together to get all information in one place.
            query = models.Project.query.join(models.Country). \
                                              join(models.Key). \
                                             filter(models.Project.expiryDate > func.now(), \
                                             models.Project.enabled == True, \
                                             models.Project.projectUrl != None, \
                                             models.Project.targetCountries == models.Country.tcid, \
                                             models.Project.targetKeys == models.Key.kid)

        ## Filter the newly joined table with the optional parameters supplied.
            if country != None:
              query = query.filter(models.Country.country == country)
              
            if number != None:
              query = query.filter(models.Key.number >= number)

            if keyword != None:
              query = query.filter(models.Key.keyword == keyword)

        ## After we retrieve our filtered results. Retrieve the entry with the
        ## highest projectCost      
            query = query.order_by(models.Project.projectCost.desc())

        ## Prepare information to send back to user.
            if query.count() != 0:
               message = { "projectName" : query[0].projectName,
                           "projectCost" : query[0].projectCost,
                           "projectUrl"  : query[0].projectUrl }
               return jsonify(message), 200
            else:
               return responseCode("no project found") , 200
    except :
        return responseCode("no project found") , 200
    
    return responseCode("no project found") , 200

## This method logs HTTP requests made to the server to $root/Requests.txt
@fapp.after_request
def after_request(response):
    # This IF avoids the duplication of registry in the log,
    # since that 500 is already logged via @app.errorhandler.
    if response.status_code != 500:
        with open(fapp.root_path + "\..\Requests.txt","a+") as writer:
            #ts = strftime('[%Y-%b-%d %H:%M]')
            s = '%s %s %s %s %s %s\n' % (datetime.now().strftime('[%Y-%b-%d %H:%M]'), request.remote_addr, request.method, request.scheme , request.full_path, response.status)
            writer.write(s)
    return response
    

## Decorated method to handle uncaught exceptions in the program to ensure the
## server keeps running if it faces a critical problem.
@fapp.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return "An error occurred within your request. Rolling back database" , 500

## Helper funtion to write to Projects.txt
def writeToProjects():
    with open(fapp.root_path + "\..\Projects.txt","a+") as writer:
            writer.write(json.dumps(request.json))
            writer.write('\n')

## Helper funtion to return a message in a json format
def responseCode(mess):
    message = { 'message' : mess }      
    resp = jsonify(message)

    return resp
