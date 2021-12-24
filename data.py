import multiprocessing as mp
import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
from time import sleep
from random import randint
import re
import wikipedia


class DataExtraction:

    def __init__(self):

        
        self.processes = int(mp.cpu_count())

        self.headers = {'Accept-Language': 'en-US, en;q=0.5'} #to fetch only English movies
        

        # All possible options for Wikipedia Plot subtitles
        possibles = ['Plot','Synopsis','Plot synopsis','Plot summary', 
                    'Story','Plotline','The Beginning','Summary',
                    'Content','Premise']

        possibles_edit = [i + 'Edit' for i in possibles]
        self.all_possibles = possibles + possibles_edit

        # Final data format
        self.movies = pd.DataFrame(columns=['movie', 'year', 'time_minute', 'certificate', 'imdb_rating', 'genre', 'cast', 'directors'])


        # In order to execute asynchronously, we need a pre-defined list of urls to fetch from.
        self.web_url = []
        genres_list = ['comedy', 'short', 'animation', 'music', 'action', 'crime', 'mystery',
                    'horror', 'documentary', 'history', 'drama', 'family', 'romance', 'adventure',
                    'fantasy', 'sci-fi', 'thriller']
        pages = np.arange(1, 1001, 50)  # Each page contains 50 movies, so we fetch ~1000 movies for each genre     
        

        for gen in genres_list:
            for page in pages: 
            #https://www.imdb.com/search/title/?title_type=feature&genres=comedy&start=1&explore=genres&ref_=adv_nxt # for only movies
                self.web_url.append('https://www.imdb.com/search/title/?genres=' + gen + '&start=' + str(page) + '&explore=genres&ref_=adv_nxt')


    def getPlot(self, movie):
        '''
        Fetch movie plots from Wikipedia using the wikipedia APIs.

        Parameters:
        Movie name - name of the movie for which the plot must be found.

        '''
        plot = ""
        try:
            wik = wikipedia.page(movie)
            print(wik)
            # for all possible titles in all_possibles list
            for j in self.all_possibles:
                # if that section does exist, i.e. it doesn't return 'None'
                if wik.section(j) != None:
                    #then that's what the plot is! Otherwise try the next one!
                    plot = wik.section(j).replace('\n','').replace("\'","")
                    #print(plot_)
        # if none of those work, or if the page didn't load from above, then plot
        # equals np.NaN
        
        except:
            plot= None

        wiki_plots = {'movie':movie,
                    'plot':plot}

        return wiki_plots

    def addPlots(self):

        # Dropping duplicate movies
        df = self.movies.drop_duplicates(subset=['movie'], keep='first')
        movie_names = df['movie'].unique()
        pool = mp.Pool()

        # pool object with number of element
        pool = mp.Pool(processes=self.processes)

        # input list
        inputs = movie_names

        # map the function to the list and pass
        # function and input list as arguments
        outputs = pool.map(self.getPlot, inputs)
        plots = pd.DataFrame(outputs)

        self.result = pd.merge(self.movies, plots, on="movie")
        self.saveData()


    def getData(self, url):

        '''
        Fetch data from the IMDb website and parse the information to extract the movie titles, year of release, duration, rating, genre, 
        cast, directors and certificates. Fetch plot from wikipedia.
        
        Parameters :
        - url : IMDb url to fetch data
        '''
        print(url)
        titles = []
        years = []
        time = []
        imdb_ratings = []
        genres = []
        actors = []
        director = []
        certificates = []

        page = requests.get(url, headers=self.headers)
        soup = BeautifulSoup(page.text, 'html.parser')
        
        # Extracting the list of 50 movies in each page
        movie_div = soup.find_all('div', class_='lister-item mode-advanced')
        
        sleep(randint(2,10))
        
        for container in movie_div:
            certificate = container.find('span', class_='certificate').text if container.p.find('span', class_='certificate') else None           
            certificates.append(certificate)
            
            # Scraping the movie's title
            name = container.h3.a.text
            titles.append(name)
            
            # Scraping the movie's year
            year = container.h3.find('span', class_='lister-item-year').text if container.h3.find('span', class_='lister-item-year') else None
            years.append(year.replace("[()^a-zA-Z]", ''))

            # Scraping the movie's length
            runtime = container.find('span', class_='runtime').text if container.p.find('span', class_='runtime') else None
            time.append(runtime)

            # Scraping the rating
            imdb = float(container.strong.text) if container.strong else None
            imdb_ratings.append(imdb)

            # Scraping the genre
            genre = container.find('span', class_='genre').text.strip() if container.p.find('span', class_='genre') else None
            genres.append(genre)

            # Scraping the actors
            details = container.find('p', class_='').text.strip()
            data = re.split(r'Stars:', details) if "Stars" in details else None        
            
            if data:
                actors.append(data[1].replace("\n",""))

                director_data = re.split('Director:|Directors:',data[0].replace("\n",""))[1] if "Director" in data[0] else ""  
                director.append(director_data.replace("|",""))
            else:
                actors.append(None)
                director.append(None)

        movies = {'movie':titles,
                            'year':years,
                            'time_minute':time,
                            'certificate':certificates,
                            'imdb_rating':imdb_ratings,
                            'genre':genres,
                            'cast':actors,
                            'directors':director}

        return movies
            

    def fetchData(self):
        '''
        Fetch data from IMDb asynchronously
        '''

        # pool object with number of element
        pool = mp.Pool(processes=self.processes)

        # input list
        inputs = self.web_url

        # map the function to the list and pass function and input list as arguments
        outputs = pool.map(self.getData, inputs)

        # Looping through the collected output to create a single dataframe
        for out in outputs:
            self.movies = self.movies.append(pd.DataFrame({
                                'movie':out["movie"],
                                'year':out["year"],
                                'time_minute':out["time_minute"],
                                'certificate':out["certificate"],
                                'imdb_rating':out["imdb_rating"],
                                'genre':out["genre"],
                                'cast':out["cast"],
                                'directors':out["directors"]}),ignore_index=True)
            
        self.addPlots()
                    
    

    def saveData(self):
        '''
        Saving the data to local csv file    
        '''

        # Saving only those results which have a plot
        self.result = self.result[self.result['plot'].notna()]
        self.result.to_csv('movieData.csv')


if __name__ == '__main__':
    '''
    Begin fetching the data
    '''
    DataExtraction().fetchData()
