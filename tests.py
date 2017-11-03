## Testing class. Uses default unittest framework introduced in the core python package
## Consists of fundamental tests. NOTE : Some of these tests are supposed to fail,
## to expose issues about the implementation

#!flask/bin/python
import os
import unittest
import requests
import json
from datetime import datetime

from config import basedir , HOST, PORT
from app import fapp, db

class TestCase(unittest.TestCase):
    N = 500

    ## Fixture method that sets up server and initializes database for the duration of tests.
    def setUp(self):
        fapp.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'test.db')
        self.fapp = fapp.test_client()
        db.create_all()

    ## Fixture method that cleans up after a testing routine
    def tearDown(self):
        db.session.remove()
        db.drop_all()

    ## TEST 1:
    ## Simple test to see if server has started
    def test_serverUp(self):     
        resp = self.fapp.get('/')
        assert resp.status_code == 200

    ## TEST 2:
    ## Tests a URL that's not on the server
    def test_BadUrl(self):
       
        project = {"enabled": True, "targetKeys": [{"number": 25, "keyword": "movies"}, {"number": 55, "keyword": "sports"}], "expiryDate": "05202018 00:00:00", "projectName": "test1", "id": 2, "creationDate": "05112017 00:00:00", "targetCountries": ["USA", "Brazil"], "projectUrl": "http:www.unity3d.com", "projectCost": 1.25}
        resp = self.fapp.post('/createprojects', data = json.dumps(project), content_type='application/json')

        assert resp.status_code == 404

    ## TEST 3:
    ## Tests whether a valid project can be sent through to create project and is accepted into the database.
    def test_createproject(self):
        
        project = {"enabled": True, "targetKeys": [{"number": 25, "keyword": "movies"}, {"number": 55, "keyword": "sports"}], "expiryDate": "05202018 00:00:00", "projectName": "test 1", "id": 2, "creationDate": "05112017 00:00:00", "targetCountries": ["USA", "Brazil"], "projectUrl": "http:www.unity3d.com", "projectCost": 1.25}
        resp = self.fapp.post('/createproject', data = json.dumps(project), content_type='application/json')
        db.session.rollback()
        assert resp.status_code == 200

    ## TEST 4:
    ## Tests whether /createproject rejects bad request methods    
    def test_createproject_BadRequestMethod(self):
        
        project = {"enabled": True, "targetKeys": [{"number": 25, "keyword": "movies"}, {"number": 55, "keyword": "sports"}], "expiryDate": "05202018 00:00:00", "projectName": "test1", "id": 2, "creationDate": "05112017 00:00:00", "targetCountries": ["USA", "Brazil"], "projectUrl": "http:www.unity3d.com", "projectCost": 1.25}
        resp = self.fapp.get('/createproject')

        assert resp.status_code == 405

    ## TEST 5:
    ## Sends a single valid project and requests its information via /requestproject
    def test_createproject_CreateOneProject(self):
        
        project = {"enabled": True, "targetKeys": [{"number": 25, "keyword": "movies"}, {"number": 55, "keyword": "sports"}], "expiryDate": "05202018 00:00:00", "projectName": "test1", "id": 1, "creationDate": "05112017 00:00:00", "targetCountries": ["USA", "Brazil"], "projectUrl": "http:www.unity3d.com", "projectCost": 1.25}

        resp = self.fapp.post('/createproject', data = json.dumps(project), content_type='application/json')
        assert resp.status_code == 200

        resp = self.fapp.get('/requestproject')
        data = json.loads(resp.get_data(as_text=True))
        assert data['projectCost'] == 1.25 and data['projectName'] == "test1" and data['projectUrl'] == "http:www.unity3d.com"

        db.session.rollback()

    ## TEST 6:
    ## Adds an expired project and ensures it doesn't get chosen.
    def test_createproject_AddExpiredProject(self):
        
        project = {"enabled": True, "targetKeys": [{"number": 25, "keyword": "movies"}, {"number": 55, "keyword": "spot"}], "expiryDate": "05202017 00:00:00", "projectName": "test1", "id": 1, "creationDate": "05112017 00:00:00", "targetCountries": ["USA", "Brazil"], "projectUrl": None, "projectCost": 1.25}

        resp = self.fapp.post('/createproject', data = json.dumps(project), content_type='application/json')
        assert resp.status_code == 200

        resp = self.fapp.get('/requestproject?keyword=spot')
        data = json.loads(resp.get_data(as_text=True))
        try:
            assert data['message'] == 'no project found'
        except:
            assert False

        db.session.rollback()

    ## TEST 7:
    ## Adds a project that is not enabled and ensure it doesn't get returned
    def test_createproject_AddDisabledProject(self):
        
        project = {"enabled": False, "targetKeys": [{"number": 25, "keyword": "movies"}, {"number": 55, "keyword": "spot"}], "expiryDate": "05202017 00:00:00", "projectName": "test1", "id": 1, "creationDate": "05112017 00:00:00", "targetCountries": ["USA", "Brazil"], "projectUrl": None, "projectCost": 1.25}

        resp = self.fapp.post('/createproject', data = json.dumps(project), content_type='application/json')
        assert resp.status_code == 200

        resp = self.fapp.get('/requestproject?keyword=spot')
        data = json.loads(resp.get_data(as_text=True))
        try:
            assert data['message'] == 'no project found'
        except:
            assert False

        db.session.rollback()

    ## TEST 9:
    ## Adds a project with a null Url and ensures it doesn't get returned.
    def test_createproject_AddNullProjectUrl(self):
        
        project = {"enabled": True, "targetKeys": [{"number": 25, "keyword": "movies"}, {"number": 55, "keyword": "spot"}], "expiryDate": "05202018 00:00:00", "projectName": "test1", "id": 1, "creationDate": "05112017 00:00:00", "targetCountries": ["USA", "Brazil"], "projectUrl": None, "projectCost": 1.25}

        resp = self.fapp.post('/createproject', data = json.dumps(project), content_type='application/json')
        assert resp.status_code == 200

        resp = self.fapp.get('/requestproject?keyword=spot')
        data = json.loads(resp.get_data(as_text=True))
        try:
            assert data['message'] == 'no project found'
        except:
            assert False

        db.session.rollback()

    ## TEST 10:
    ## Creates a large amount of projects and sends them to the server and
    ## requests them back.
    def test_createproject_CreateManyProjects(self):
        #N = 50
        for i in range(1,self.N):
            project = {"enabled": True, "targetKeys": [{"number": 25, "keyword": "movies"}, {"number": 55, "keyword": "sports"}], "expiryDate": "05202018 00:00:00", "projectName": "test %d" % i, "id": i, "creationDate": "05112017 00:00:00", "targetCountries": ["USA", "Brazil"], "projectUrl": "http:www.unity3d.com", "projectCost": i+0.5}

            resp = self.fapp.post('/createproject', data = json.dumps(project), content_type='application/json')
            assert resp.status_code == 200

        for j in range(1,self.N):
            resp = self.fapp.get('/requestproject?projectid=' + str(j))
            data = json.loads(resp.get_data(as_text=True))
            assert data['projectCost'] == j + 0.5 and data['projectName'] == "test " + str(j)
        
        resp = self.fapp.get('/requestproject')
        data = json.loads(resp.get_data(as_text=True))
        assert data['projectCost'] == (self.N - 1) + 0.5 and data['projectName'] == "test "+ str(self.N - 1)
        db.session.rollback()

    ## TEST 11:
    ## Sends an invalid project field to the server.
    def test_createproject_BadProjectArgsName(self):
        
        project = {"enab": True, "targetKeys": [{"number": 25, "keyword": "movies"}, {"number": 55, "keyword": "sports"}], "expiryDate": "05202018 00:00:00", "projectName": "test1", "id": 3, "creationDate": "05112017 00:00:00", "targetCountries": ["USA", "Brazil"], "projectUrl": "http:www.unity3d.com", "projectCost": 1.25}

        resp = self.fapp.post('/createproject', data = json.dumps(project), content_type='application/json')
        assert resp.status_code == 400   

    ## TEST 12:
    ## Sends valid project fields with invalid field values to the server.
    def test_createproject_BadProjectArgsValues(self):
        
        project = {"enable": True, "targetKeys": [{"number": 25, "keyword": "movies"}, {"number": 55, "keyword": "sports"}], "expiryDate": "05202018 00:00:00", "projectName": "test1", "id": 4, "creationDate": "05112017 00:00:00", "targetCountries": ["USA", "Brazil"], "projectUrl": "http:www.unity3d.com", "projectCost": "alf"}

        resp = self.fapp.post('/createproject', data = json.dumps(project), content_type='application/json')
        assert resp.status_code == 400

    ## TEST 13:
    ## Sends an invalid project to the server supplied with not enough fields to specify a project.
    def test_createproject_NotEnoughArgs(self):
        
        project = {"targetKeys": [{"number": 25, "keyword": "movies"}, {"number": 55, "keyword": "sports"}]}

        resp = self.fapp.post('/createproject', data = json.dumps(project), content_type='application/json')
        assert resp.status_code == 400

    ## TEST 14:
    ## Sends additional Json fields with an otherwise valid project object to the server.
    def test_createproject_ExtraUnnecessaryJsonAttributes(self):
        
        project = {"orange": "Because why not", "enabled": True, "targetKeys": [{"number": 25, "keyword": "movies"}, {"number": 55, "keyword": "sports"}], "expiryDate": "05202018 00:00:00", "projectName": "test1", "id": 2, "creationDate": "05112017 00:00:00", "targetCountries": ["USA", "Brazil"], "projectUrl": "http:www.unity3d.com", "projectCost": 1.25}
        resp = self.fapp.post('/createproject', data = json.dumps(project), content_type='application/json')
        assert resp.status_code != 200

        db.session.rollback()
    ## TEST 15:
    ## Requests a project with no arguments (returns *valid project with highest projectCost)
    def test_requestproject_NoArgs(self):     
        #N = 50
        for i in range(1,self.N):
            project = {"enabled": True, "targetKeys": [{"number": 25, "keyword": "movies"}, {"number": 55, "keyword": "sports"}], "expiryDate": "05202018 00:00:00", "projectName": "test %d" % i, "id": i, "creationDate": "05112017 00:00:00", "targetCountries": ["USA", "Brazil"], "projectUrl": "http:www.unity3d.com", "projectCost": i+0.5}
            resp = self.fapp.post('/createproject', data = json.dumps(project), content_type='application/json')
            assert resp.status_code == 200

        resp = self.fapp.get('/requestproject')
        data = json.loads(resp.get_data(as_text=True))
        assert data['projectCost'] == (self.N - 1) + 0.5 and data['projectName'] == "test " + str(self.N - 1)
        db.session.rollback()

    ## TEST 16:
    ## Requests a project with a specefied projectid
    def test_requestproject_ProjectID(self):     
        #N = 50
        for i in range(1,self.N):
            project = {"enabled": True, "targetKeys": [{"number": 25, "keyword": "movies"}, {"number": 55, "keyword": "sports"}], "expiryDate": "05202018 00:00:00", "projectName": "test %d" % i, "id": i, "creationDate": "05112017 00:00:00", "targetCountries": ["USA", "Brazil"], "projectUrl": "http:www.unity3d.com", "projectCost": i+0.5}
            resp = self.fapp.post('/createproject', data = json.dumps(project), content_type='application/json')
            assert resp.status_code == 200

        for j in range(1,self.N):
            resp = self.fapp.get('/requestproject?projectid=' + str(j))
            data = json.loads(resp.get_data(as_text=True))
            assert data['projectCost'] == j + 0.5 and data['projectName'] == "test " + str(j)

        db.session.rollback()

    ## TEST 17:
    ## Requests the project with the highest Cost with a particular Country
    def test_requestproject_Country(self):     
        #N = 50
        for i in range(1,self.N):
            project = {"enabled": True, "targetKeys": [{"number": 25, "keyword": "movies"}, {"number": 55, "keyword": "sports"}], "expiryDate": "05202018 00:00:00", "projectName": "Incorrect Answer", "id": i, "creationDate": "05112017 00:00:00", "targetCountries": ["NotUSA", "Brazil"], "projectUrl": "http:www.unity3d.com", "projectCost": i+0.5}
            resp = self.fapp.post('/createproject', data = json.dumps(project), content_type='application/json')
            assert resp.status_code == 200

        project = {"enabled": True, "targetKeys": [{"number": 25, "keyword": "movies"}, {"number": 55, "keyword": "sports"}], "expiryDate": "05202018 00:00:00", "projectName": "Correct Answer", "id": self.N, "creationDate": "05112017 00:00:00", "targetCountries": ["USA", "Brazil"], "projectUrl": "http:www.unity3d.com", "projectCost": 10000}
        resp = self.fapp.post('/createproject', data = json.dumps(project), content_type='application/json')
        assert resp.status_code == 200
        
        resp = self.fapp.get('/requestproject?country=USA')
        data = json.loads(resp.get_data(as_text=True))
        assert data['projectCost'] == 10000 and data['projectName'] == "Correct Answer"

        db.session.rollback()

    ## TEST 18:
    ## Requests the project with the highest Cost with a target key number atleast of a vertain number
    def test_requestproject_Number(self):     
        #N = 50
        for i in range(1,self.N):
            project = {"enabled": True, "targetKeys": [{"number": self.N + 1000, "keyword": "movies"}, {"number": i, "keyword": "sports"}], "expiryDate": "05202018 00:00:00", "projectName": "test %d" % i, "id": i, "creationDate": "05112017 00:00:00", "targetCountries": ["USA", "Brazil"], "projectUrl": "http:www.unity3d.com", "projectCost": i+0.5}
            resp = self.fapp.post('/createproject', data = json.dumps(project), content_type='application/json')
            assert resp.status_code == 200

        resp = self.fapp.get('/requestproject?number=1')
        data = json.loads(resp.get_data(as_text=True))
        assert data['projectCost'] == (self.N - 1) + 0.5 and data['projectName'] == "test " + str(self.N - 1)

        db.session.rollback()

    ## TEST 19:
    ## Requests the project with the highest Cost with a target key keyword
    def test_requestproject_Keywords(self):     
        #N = 50
        for i in range(1,self.N):
            project = {"enabled": True, "targetKeys": [{"number": self.N + 1000, "keyword": "movies %d" % i}, {"number": i, "keyword": "sports"}], "expiryDate": "05202018 00:00:00", "projectName": "test %d" % i, "id": i, "creationDate": "05112017 00:00:00", "targetCountries": ["USA", "Brazil"], "projectUrl": "http:www.unity3d.com", "projectCost": i+0.5}
            resp = self.fapp.post('/createproject', data = json.dumps(project), content_type='application/json')
            assert resp.status_code == 200

        for j in range(1,self.N):
            resp = self.fapp.get('/requestproject?keyword=movies ' + str(j))
            data = json.loads(resp.get_data(as_text=True))
            assert data['projectCost'] == j + 0.5 and data['projectName'] == "test " + str(j)

        db.session.rollback()

    ## TEST 20:
    ## Requests the project with the highest Cost with a combination of the optional paramters to /requestproject
    def test_requestproject_Combination(self):     
        #N = 50
        for i in range(1,self.N):
            project = {"enabled": True, "targetKeys": [{"number": self.N + 1000, "keyword": "movies%d" % i}, {"number": i, "keyword": "sports"}], "expiryDate": "05202018 00:00:00", "projectName": "test %d" % i, "id": i, "creationDate": "05112017 00:00:00", "targetCountries": ["USA", "Brazil"], "projectUrl": "http:www.unity3d.com", "projectCost": i+0.5}
            resp = self.fapp.post('/createproject', data = json.dumps(project), content_type='application/json')
            assert resp.status_code == 200

        resp = self.fapp.get('/requestproject?keyword=movies'+str(int(self.N/2))+'&number='+str(int(self.N/2)))
        data = json.loads(resp.get_data(as_text=True))
        assert data['projectCost'] == (int(self.N/2)) + 0.5 and data['projectName'] == "test " + str(int(self.N/2))

        db.session.rollback()

    ## TEST 21:
    ## Requests the project with the highest Cost with a target key number atleast of a vertain number
    def test_requestproject_NoProjectReturned(self):     
        #N = 50
        for i in range(1,self.N):
            project = {"enabled": True, "targetKeys": [{"number": self.N + 1000, "keyword": "movies%d" % i}, {"number": i, "keyword": "sports"}], "expiryDate": "05202018 00:00:00", "projectName": "test %d" % i, "id": i, "creationDate": "05112017 00:00:00", "targetCountries": ["USA", "Brazil"], "projectUrl": "http:www.unity3d.com", "projectCost": i+0.5}
            resp = self.fapp.post('/createproject', data = json.dumps(project), content_type='application/json')
            assert resp.status_code == 200

        resp = self.fapp.get('/requestproject?keyword=mov'+str(int(self.N/2))+'&number='+str(int(self.N/2)))
        data = json.loads(resp.get_data(as_text=True))
        assert data['message'] == 'no project found'

        db.session.rollback()

    ## TEST 22:
    ## Requests a project with invalid url arguments 
    def test_requestproject_BadURLArguments(self):     
        #N = 50
        for i in range(1,self.N):
            project = {"enabled": True, "targetKeys": [{"number": self.N + 1000, "keyword": "movies%d" % i}, {"number": i, "keyword": "sports"}], "expiryDate": "05202018 00:00:00", "projectName": "test %d" % i, "id": i, "creationDate": "05112017 00:00:00", "targetCountries": ["USA", "Brazil"], "projectUrl": "http:www.unity3d.com", "projectCost": i+0.5}
            resp = self.fapp.post('/createproject', data = json.dumps(project), content_type='application/json')
            assert resp.status_code == 200

        resp = self.fapp.get('/requestproject?basketballers=KobeBryant')
        assert resp.status_code != 200

        db.session.rollback()

    ## TEST 23:
    ## Requests a project with "None" (python null) as one of its optional paramters 
    def test_requestproject_NoneWordArg(self):     
        #N = 50
        for i in range(1,self.N):
            project = {"enabled": True, "targetKeys": [{"number": self.N + 1000, "keyword": "movies%d" % i}, {"number": i, "keyword": "sports"}], "expiryDate": "05202018 00:00:00", "projectName": "test %d" % i, "id": i, "creationDate": "05112017 00:00:00", "targetCountries": ["USA", "Brazil"], "projectUrl": "http:www.unity3d.com", "projectCost": i+0.5}
            resp = self.fapp.post('/createproject', data = json.dumps(project), content_type='application/json')
            assert resp.status_code == 200

        resp = self.fapp.get('/requestproject?keyword=None')
        assert resp.status_code == 200

        db.session.rollback()

    ## TEST 24:
    ## Requests a project with invalid url arguments 
    def test_requestproject_NegativeProjectID(self):
        project = {"enabled": True, "targetKeys": [{"number": 25, "keyword": "movies"}, {"number": 55, "keyword": "sports"}], "expiryDate": "05202018 00:00:00", "projectName": "test-1", "id": -1, "creationDate": "05112017 00:00:00", "targetCountries": ["USA", "Brazil"], "projectUrl": "http:www.unity3d.com", "projectCost": 1.25}

        resp = self.fapp.post('/createproject', data = json.dumps(project), content_type='application/json')
        assert resp.status_code == 200

        resp = self.fapp.get('/requestproject')
        data = json.loads(resp.get_data(as_text=True))
        assert data['projectCost'] == 1.25 and data['projectName'] == "test-1" and data['projectUrl'] == "http:www.unity3d.com"

    ## TEST 25:
    ## Sees if projects that are added to the database are being written to Projects.txt 
    def test_ProjectLog_WritingToProjects(self):
        #N = 50
        for i in range(1,self.N):
            project = {"enabled": True, "targetKeys": [{"number": 25, "keyword": "movies"}, {"number": 55, "keyword": "sports"}], "expiryDate": "05202018 00:00:00", "projectName": "test %d" % i, "id": i, "creationDate": "05112017 00:00:00", "targetCountries": ["USA", "Brazil"], "projectUrl": "http:www.unity3d.com", "projectCost": i+0.5}

            resp = self.fapp.post('/createproject', data = json.dumps(project), content_type='application/json')
            assert resp.status_code == 200
            
        with open(os.path.join(basedir, 'Projects.txt'), 'rb') as f:
            for line in f:
                data = json.loads(str(line,'UTF-8'))
                try:
                    data['id'] != None
                except:
                    assert False

        db.session.rollback()

    ## TEST 26:
    ## Sees if server requests are being logged to Requests.txt
    def test_RequestLog_WritingToRequest(self):
        #N = 50
        resp = self.fapp.get('/')
        assert resp.status_code == 200
            
        with open(os.path.join(basedir, 'Requests.txt'), 'rb') as f:
            for line in f:
                pass
        last = str(line, 'UTF-8')
        expected = str(datetime.now().strftime('[%Y-%b-%d %H:%M]'))+ " " + HOST + " GET http /? 200 OK\r\n"
        assert last == expected
            
                  
if __name__ == '__main__':
    unittest.TestLoader.sortTestMethodsUsing = None
    try:
        os.remove(os.path.join(basedir, 'Projects.txt'))
    except OSError:
        pass
    unittest.main(verbosity=2)


