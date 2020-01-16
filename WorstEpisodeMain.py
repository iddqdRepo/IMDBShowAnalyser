import requests
import bs4
from itertools import chain
import tabulate
import shelve
import logging
from matplotlib import pyplot as plt
from operator import itemgetter

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logging.disable(logging.DEBUG)
'''
    
This Program
    organise into one big dict for general calculations
    leave in nested lists for season/episode specific calculations
    
Output
    Which season is the worst (ratings of episodes in a season divided by number of them)
    Which episode is the worst (loop through and store the lowest episode in a list, if a new episode is lower, replace the old) 
    Which episode is the best
    Which season is best
    
'''

gotTag = 'tt0944947'
peakyBlindersTag = 'tt2442560'
simpsonsTag = 'tt0096697'
showToSearch = 'Game of Thrones'

# --------------TAGS FROM SHELF FILE
#shelfFile = shelve.open('TvSeriesData')  # open shelf data file
#tvshows = list(chain.from_iterable(list(shelfFile.values())))  # get list of values from file and un-nest list
# next(item for item in tvshows if item["name"] == "Supernatural")  # searching tvshows

#soup = bs4.BeautifulSoup(res1.text, 'html.parser')


def episoderating(url):
    site = url
    logging.debug('URL is %s: ' % (url))
    res = requests.get(url)
    res.raise_for_status()
    soup = bs4.BeautifulSoup(res.text, 'html.parser')
    episodeRating = soup.select('.ipl-rating-star.small .ipl-rating-star__rating')  # search for star rating
    episode_rating_list = [title.text for title in episodeRating]  #
    logging.info("episode rating %s:" % episode_rating_list)
    return episode_rating_list


def episodenames(url):
    logging.debug('URL is %s: ' % (url))
    res = requests.get(url)
    res.raise_for_status()
    soup = bs4.BeautifulSoup(res.text, 'html.parser')
    episode_name = soup.select('#episodes_content strong a')
    episode_name_list = [title.text for title in episode_name]
    episode_name_list_clean = []
    for i in range(len(episode_name_list)):
        if "Rate" in episode_name_list[i] or episode_name_list[i].strip() == "":
            continue
        else:
            episode_name_list_clean.append(episode_name_list[i])

    return episode_name_list_clean


def whichseason(url):
    logging.debug('URL is %s: ' % (url))
    res = requests.get(url)
    res.raise_for_status()
    soup = bs4.BeautifulSoup(res.text, 'html.parser')
    which_season = soup.select('#episode_top')
    return logging.info(which_season[0].get_text().strip('Season').strip())  # returns 'Season X' but removes the word Season and strips again to remove the space, better than [-1:] which wont work for double digit sesaons


# Old Season Check - redundant
def finalseasoncheck(url):
    logging.debug('URL is %s: ' % (url))
    res = requests.get(url)
    res.raise_for_status()
    soup = bs4.BeautifulSoup(res.text, 'html.parser')
    loadNextEpisodes = soup.select('#load_next_episodes')
    load_Next_Episodes_list = [title.text for title in loadNextEpisodes]  # if this is blank, there are no more seasons
    if len(load_Next_Episodes_list) != 0:
        logging.debug(load_Next_Episodes_list)
        logging.info("True: new season")
        print(load_Next_Episodes_list)
        return True
    else:
        logging.info("False: Final season")
        return False

# Returns the total number of seasons in the show
def totalNumOfSeasons(url):
    res = requests.get(url)
    res.raise_for_status()
    soup = bs4.BeautifulSoup(res.text, 'html.parser')
    loadNextEpisodes = soup.select('.clear+ div a:nth-child(1)')
    load_Next_Episodes_list = [title.text for title in loadNextEpisodes]
    return int(load_Next_Episodes_list[0])


# Returns the name of the show on the page
def showName(url):
    res = requests.get(url)
    res.raise_for_status()
    soup = bs4.BeautifulSoup(res.text, 'html.parser')
    name = soup.select('.parent a')
    return name[0].text

# Takes in a tag and does the searching
# This is not needed to be called if the data is already in PreviouslyAnalysedShows shelf
# need to look up show tag in TvSeriesData shelf - Pass as an argument to Main
def findAndSearch(showTag):
    checkingSeasonNumber = 1
    # get number of episodes on page (as iterable for loop)
    showUrl = 'https://www.imdb.com/title/' + showTag
    shelfFile = shelve.open('TestTvShowData')  # open shelf data file

    #showName(showUrl + '/episodes?season=' + str(checkingSeasonNumber))

    aggregatedData = []
    while checkingSeasonNumber != totalNumOfSeasons(showUrl)+1:
        aggregatedData.append(episodenames(showUrl + '/episodes?season=' + str(checkingSeasonNumber)))
        aggregatedData.append(episoderating(showUrl + '/episodes?season=' + str(checkingSeasonNumber)))

        #print(showUrl + '/episodes?season=' + str(checkingSeasonNumber))
        checkingSeasonNumber += 1

    print(aggregatedData)
    shelfFile[showName(showUrl + '/episodes?season=1')] = aggregatedData


def graph(showName):
    tag = ''
    sf = shelve.open('TestTvShowData')
    print(list(sf.keys()))
    # Checking if it's in the shelf file
    if showName in list(sf.keys()):
        values = sf[showName]
    allRatings = []  # values[i] for i in range(1, len(values), 2)
    allNames = []
    for i in range(1, len(values), 2):
        for x in values[i]:
            allRatings.append(float(x))
    for i in range(0, len(values), 2):
        for x in values[i]:
            allNames.append(x)

    x = allNames
    y = allRatings
    plt.bar(x, y)
    x_pos = range(len(x))
    plt.xticks(x_pos, x, rotation=90)
    plt.title(showName + " - Episodes by Rating")
    #plt.xlabel("Episode")
    plt.ylabel("Rating")
    plt.show()

    print("all ratings list = %s" % allRatings)
    print("all allNames list = %s" % allNames)
    print(values[1][0])
    print(float(values[1][0]))
    print(type(float(values[1][0])))


# Outputs the 'best episode' - currently opens the shelf file and uses the only piece of data in it
def bestEpisode():
    sf = shelve.open('PreviouslyAnalysedShows')
    print("sf.keys %s" % list(sf.keys()))
    values = list(chain.from_iterable(list(sf.values())))
    print(values)
    allRatings = []
    allNames = []
    dictshow = []
    for i in range(1, len(values), 2):
        for x in values[i]:
            allRatings.append(float(x))
    for i in range(0, len(values), 2):
        for x in values[i]:
            allNames.append(x)
    l = 0
    while l <(len(allRatings)):
        dictshow.append({'Name': allNames[l], 'Rating':allRatings[l]})
        l+=1
    print(dictshow)
    sortedDictShowList = sorted(dictshow, key=itemgetter('Rating'), reverse=True)
    print(sortedDictShowList)
    print('Best episode is %s' % sortedDictShowList[0])


def main():
    previousShelf = shelve.open('TestTvShowData')
    shelfFile = shelve.open('TvSeriesData')
    tagDataShows = list(chain.from_iterable(list(shelfFile.values())))
# Ask which show to analyse
    print("Which Show do you want to analyse? (Case Sensitive)")
# Take input
    givenShow = input()
# Search if show has already been analysed and stored in PreviouslyAnalysedShows shelf and Skip finding
    if givenShow in list(previousShelf.keys()):
        graph(givenShow)
# If not, find tag from TvSeriesData shelf & use it as the argument for findAndSearch(showTag)
    if givenShow not in list(previousShelf.keys()):
        logging.info("In Else")

        for i in range(len(tagDataShows)):
            if tagDataShows[i]['ShowName'] == givenShow:
                logging.info("Checking if")
                tag = tagDataShows[i].get('ShowLink')
                logging.info(tagDataShows[i].get('ShowLink'))

        #main(tag)
#comment1

# Just Testing Stuff
def testtvshows():

    #use this in graph

    sf = shelve.open('TestTvShowData')
    print(list(sf.keys()))
    touse = ''
    # Checking if it's in the shelf file
    if 'Game of Thrones' in list(sf.keys()):
        print("yeeeeeeeeee")
        touse = sf['Game of Thrones']

    print(touse)
    allRatings = []  # values[i] for i in range(1, len(values), 2)
    allNames = []
    for i in range(1, len(touse), 2):
        for x in touse[i]:
            allRatings.append(float(x))
    for i in range(0, len(touse), 2):
        for x in touse[i]:
            allNames.append(x)
    print("all ratings list = %s" % allRatings)
    print("all allNames list = %s" % allNames)

    values = list(chain.from_iterable(list(sf.values())))
    #print(sf['Game of Thrones'])
    #print(sf['Peaky Blinders'])

def testest():
    shelfFile = shelve.open('TvSeriesData')
    print("Which Show do you want to analyse? (Case Sensitive)")
    toSearch = input()
    tvhows = list(chain.from_iterable(list(shelfFile.values())))
    for i in range(len(tvhows)):
        if tvhows[i]['ShowName'] == toSearch:
            print(tvhows[i].get('ShowLink'))

#testtvshows()
#testest()
main()
#findAndSearch('tt2442560')
#graph('Game of Thrones')
#bestEpisode()




'''
    
  
'''




# totalseasons('https://www.imdb.com/title/' + gotTag + '/episodes?season=')
# episoderating('https://www.imdb.com/title/' + gotTag + '/episodes?season=1')  # returns list of ratings
# episodenames('https://www.imdb.com/title/' + gotTag + '/episodes?season=1')  # returns list of ep names
# whichseason('https://www.imdb.com/title/' + gotTag + '/episodes?season=1')  # returns season number
# finalseasoncheck('https://www.imdb.com/title/' + gotTag + '/episodes?season=1')  # returns True if another Season











    # Loop through based on number of episodes
#    for i in range(len(episode_name_list_clean)):
#        logging.info(episode_name_list_clean[i])


# Store episode name and star rating in a dict list
# If another season: Change URL https://www.imdb.com/title/SHOWTAG/episodes?season=NEXTEPISODENUMBER and repeat
# If no other season(else): Break



# dict = {"Name": file, "Size": str(convert_size(os.path.getsize(name))), "Created": str(time.ctime(os.path.getmtime(name)))}


def oldGraph():
    sf = shelve.open('TestTvShowData')
    print(list(sf.keys()))
    values = list(chain.from_iterable(list(sf.values())))
    allRatings = [] # values[i] for i in range(1, len(values), 2)
    allNames = []
    for i in range(1, len(values), 2):
        for x in values[i]:
                allRatings.append(float(x))
    for i in range(0, len(values), 2):
        for x in values[i]:
                allNames.append(x)

'''
    for i in range(0, len(values), 2):
        aggNames.append(values[i])
        aggRatings.append(values[i])
        print(i)
    for i in range(0, len(values), 2):
        aggNames.append(values[i])
        aggRatings.append(values[i])
        print(i)
        
        
episode_name_list_clean_comprehension = [
    episode_name_list[i] for i in range(len(episode_name_list)) 
    if "Rate" not in episode_name_list[i] and episode_name_list[i].strip() != ""
]

#OLD EPISODE LIST NON COMPREHENSION

episode_name_list_clean = []
for i in range(len(episode_name_list)):
    if "Rate" in episode_name_list[i] or episode_name_list[i].strip() == "":
        continue
    else:
        episode_name_list_clean.append(episode_name_list[i])
        
        
        

def oldmain():
    url = 'https://www.imdb.com/chart/toptv/?ref_=nv_tvv_250'
    res = requests.get(url)
    res.raise_for_status()
    soup = bs4.BeautifulSoup(res.text, 'html.parser')

    movies = soup.select('.titleColumn a')
    movies_titles = [title.text for title in movies]
    movies_links = ["http://imdb.com" + title["href"] for title in movies]  #title["href"] gets the href value from movies e.g. <a href="/title/tt0185906/" title="Band of Brothers"</a>
    print(movies_links)
    #for titles in movies_titles:
    print(movies_titles)

'''
