# https://stackoverflow.com/questions/69397039/pymongo-ssl-certificate-verify-failed-certificate-has-expired-on-mongo-atlas
from api import configuration
import pymongo
client  = pymongo.MongoClient(configuration.MONGO_URI)
db = client.get_database(configuration.MONGO_DB)