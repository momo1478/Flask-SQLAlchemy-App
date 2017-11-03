from config import HOST, PORT

from app import fapp

if HOST != None and PORT != None:
    fapp.run(debug = True, host = HOST, port = PORT)
else:
    fapp.run(debug = True)
