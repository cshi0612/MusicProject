import firebase_admin
from firebase_admin import credentials, firestore


class Database:
    def __init__(self):
        # Replace the projectID eg.
        # self.bucket_name = 'codingminds.appspot.com'
        # self.bucket_name = '<projectID>.appspot.com'

        self.collection = 'History'

        # You need to download the serviceaccount.json
        # Get your service key from firebase
        self.fb_cred = 'musichistory-d9328-firebase-adminsdk-uezhc-5312a3bf79.json'
        cred = credentials.Certificate(self.fb_cred)
        # firebase_admin.initialize_app(cred,
        # {'storageBucket': self.bucket_name})
        firebase_admin.initialize_app(cred)
        self.db = firestore.client()  # this connects to our Firestore database

    def set_events(self, collection: str, data: dict):
        collection = self.db.collection(collection)  # opens collection
        for month, events in data.items():
            print("Processing month: ", month)
            doc = collection.document(month)  # specifies the  document
            doc.set(events)

    def add_data(self, data: dict):
        doc_ref = self.db.collection(self.collection).document()
        doc_ref.set(data)

    def read_data(self):
        collection_ref = self.db.collection(self.collection)
        docs = collection_ref.stream()
        res = list()
        for doc in docs:
            res.append(doc.to_dict())
        return res