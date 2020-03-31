import pymongo

#insert data
myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["flightdb"]
mycol = mydb["passengers2"]

#mydict = {"PNR": "1078", "month":1,"airline":"VX","schdep":1705,"deptime":1725.0,"depdelay":20.0,"tout":14.0,"woff":1739.0,"schtime":160.0,"dist":954,"scharr":1945,"oair":"LAX","dair":"SEA","etime":154.25974}

x = mycol.insert_one(mydict)