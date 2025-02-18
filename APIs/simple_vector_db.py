
from sentence_transformers import SentenceTransformer, models, util
from scipy.spatial.distance import cosine
from scipy.spatial.distance import euclidean
import uuid
from datetime import datetime

class SimpleVectorDB:
    def __init__(self):
        self.db = {}
        self.model = SentenceTransformer("multi-qa-MiniLM-L6-cos-v1")
        self.indexes = {}
        self.indexes["timestamp"] = [] # id, timestamp

    def create_collection(self, collection_name):
        print("Creating collection: ", collection_name)
        self.db[collection_name] = {}

    def remove_collection(self, collection_name):
        print("Removing collection: ", collection_name)
        del self.db[collection_name]

    def insert_into_collection(self, collection_name, title, text, vector, id=None, timestamp=None):
        print("Inserting into collection: ", collection_name)
        if id is None:
            # random 32 byte string
            id = uuid.uuid4().hex
        if timestamp is None:
            timestamp = datetime.now()
        self.db[collection_name][id] = {
            'title': title, 
            'text': text, 
            'vector': vector,
            'id': id,
            'timestamp': timestamp
        }

        self.indexes["timestamp"].append(id)

    def get_by_time_range(self, collection_name, start, end):
        results = []
        # todo implement binary search
        for id in self.indexes.timestamp:
            doc = self.db[collection_name].get(id)
            if doc['timestamp'] > start and doc['timestamp'] < end:
                results.append(doc)
        return results

    def delete_from_collection(self, collection_name, id):
        print("Deleting from collection: ", collection_name)
        del self.db[collection_name][id]

    def get_by_id(self, collection_name, id):

        return self.db[collection_name].get(id)

    def get_by_title(self, collection_name, title):
        for doc in self.db[collection_name].values():
            if doc['title'] == title:
                return doc
        return None
    
    def get_embedding(self, text):
        return self.model.encode(text)

    def vector_search_cos(self, collection_name, vector, top_n=1, start=0, end=0):
        print("Searching collection: ", collection_name)

        to_search = []
        if start != 0 and end != 0 and start < end:
            to_search = self.get_by_time_range(collection_name, start, end)
        else:
            to_search = self.db[collection_name].items()
        results = []
        for id, doc in to_search:
            score = self.get_cos_simmilarity(doc['vector'], vector)
            results.append((score, doc))

        return sorted(results, key=lambda x: x[0], reverse=True)[:top_n]

    def vector_search_euclidean(self, collection_name, vector, top_n):
        print("Searching collection: ", collection_name)
        results = []
        #print length of collection
        print(f"collection length: {len(self.db[collection_name].items())}")
        
        for id, doc in self.db[collection_name].items():
            score = self.get_euclidean_distance(doc['vector'], vector)
            results.append((score, doc))
        # for each in results: print text
        for each in sorted(results, key=lambda x: x[0], reverse=False):
            print(each[1]['text'])
            try:
                each[1]['vector'] = each[1]['vector'].tolist() 
            except:
                pass
        return sorted(results, key=lambda x: x[0], reverse=False)[:int(top_n)]
    
    def get_cos_simmilarity(self, v1, v2):
        return 1 - cosine(v1, v2)
    
    def get_euclidean_distance(self, v1, v2):
        return euclidean(v1, v2)
    
    def collection_exists(self, collection_name):
        return collection_name in self.db