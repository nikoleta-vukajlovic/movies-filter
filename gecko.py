import requests
from requests.auth import HTTPBasicAuth
import sys
import pymongo

def parse_args():
    if len(sys.argv) <= 1:
        print('Enter the movie title in the command line arguments')
        exit()

    args = sys.argv[1:]
    title = False

    for arg in args:
        if arg.startswith('t='):
            title = True
    
    if not title:
        print('Enter the movie title in the command line arguments')
        exit()

    genre = ""
    rating = ""

    for arg in args:
        if arg.startswith('imdbRating='):
            rating = arg[11:]
        elif arg.startswith('genre='):
            genre = arg[6:]

    titles = []

    for i in range(len(args)):
        if args[i].startswith('t='):
            title = args[i][2:]
            i += 1
            while (i < len(args) and not args[i].startswith('t=') and not args[i].startswith('genre=') and not args[i].startswith('imdbRating')):
                title += " " + args[i]
                i += 1
            titles.append(title)
            
    return genre, rating, titles

def main():

    genre, rating, titles = parse_args()

    myclient = pymongo.MongoClient("localhost", 27017)

    mydb = myclient.omdb
    mycol = mydb['movies']

    URL = "http://www.omdbapi.com/?apikey=8f0d9811&"

    db = False
    req = False

    with open('output.txt', 'w') as f:
        for i in range(len(titles)):

            mydoc = mycol.find_one({"Title" : {"$regex" : titles[i], "$options":"i"}}, {"_id":0})

            if mydoc:
                data = mydoc
                db = True
            else:
                u = URL + 't=' + titles[i]
                r = requests.get(url = u) 
                data = r.json()
                mycol.insert_one(data)
                req = True

            write_movie = False

            if genre and rating:
                if genre in data['Genre'] and float(data['imdbRating']) < float(rating):
                    write_movie = True
            elif genre and genre in data['Genre']:
                write_movie = True
            elif rating and float(data['imdbRating']) < float(rating):
                write_movie = True
            elif not genre and not rating:
                write_movie = True

            if write_movie:
                if db:
                    f.write(str(data) + "\n\n")
                else:
                    f.write(r.text + "\n\n")

if __name__ == "__main__":
    main()