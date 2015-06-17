## Private Directory
The `private` directory which is for storing stuff like api keys that you don't want to share with other people but need for your app to run.

### MongoClientConnection.py
```py
from pymongo import MongoClient

class MongoClientConnection:
    def __init__(self):
        self.connection = MongoClient("<MongoDB URI>")
```

