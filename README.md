# Python scraper to collect movie data from IMDb and Wikipedia 

This repo contains the script to obtain approximately 17k movies from IMDb and their corresponding plots from Wikipedia. The scraper makes use of BeautifulSoup and Wikipedia APIs and utilises multi-threading to decrease the run time.

  
  

###  1. IMDb data - https://www.imdb.com  

The website is well known for its collection of movie and tv shows - amounting to approximately 8 million titles. Since the IMDb APIs provide a limited amount of data, we use the Beautiful Soup library to directly scrape the movie details from the website.

The data collection script extracts the following details -
* Show title
* Year of release
* Duration
* Rating
* Genre
* Cast
* Director
* Certification  

Although plots are available on IMDb, they only provide a general outline of the movie. In order to improve the accuracy of our predictions, it is important to have a detailed summary of the movie itself - available on Wikipedia.

  

###  2. Wikipedia data - https://wikipedia.org  

Since Wikipedia relies on crowdsourcing for its information, we are given access to in-depth movie summaries that provide us with more data when compared to IMDb. Extracting these plots allows us to increase the amount of information being fed to the model, and therefore, create better predictions. The data is downloaded using the wikipedia APIs.


## Usage - 

* The script runs on `Python3` and all required packages are available in the `requirements.txt` file. 
* The code uses multi-threading for faster execution time, and by default uses `multiprocessing.cpu_count()`. 
* A fixed list of 17 genres are specified in `genres_list`.

*Note: Some movies are avaialbe in multiple genre lists, so we first extract all titles and then download wikipedia plots for only the unique movie list.*
