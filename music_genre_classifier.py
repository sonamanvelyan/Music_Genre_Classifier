import bs4 as BeautifulSoup
import pprint
import urllib.request, urllib.parse

def getBase():
	return "https://en.wikipedia.org"

def listUnion(list1, list2):
	return list(set(list1 + list2))

def listIntersection(list1, list2):
	result = []
	for l in list1:
		if l in list2:
			result.append(l)
	return result

def getGroupList(url):
	result = []
	dest = urllib.parse.urljoin(getBase(), url)

	# sending get request and saving the response as response object
	page = urllib.request.urlopen(dest)

	# cook the soup
	soup = BeautifulSoup.BeautifulSoup(page, features="html.parser")

	# extract Groups
	mwPages = soup.find("div", {"id": "mw-pages"})

	if not mwPages is None:
		divs = mwPages.find_all("div", {"class": "mw-content-ltr"})

		for d in divs:
			hyperLinks = d.find_all("a")
			for h in hyperLinks:
				result = result + [(h.string, h["href"])]
	
	# extract Subcategories
	divs = [div for div in soup.find_all("div", {"class": "CategoryTreeItem"})]

	if divs != []:
		for div in divs:
			hyperLink = div.find("a")
			result = result + getGroupList(hyperLink["href"])
	
	# remove duplicate elements
	result = list(set(result))

	result.sort()

	return result

def getGenresList(url):
	result = []

	dest = urllib.parse.urljoin(getBase(), url)

	# sending get request and saving the response as response object
	page = urllib.request.urlopen(dest)

	# cook the soup
	soup = BeautifulSoup.BeautifulSoup(page, features="html.parser")

	texts = soup.find_all(text=True)
	for text in texts:
		if text.parent.name == 'th' and text == 'Genres':
			hyperLinks = text.parent.parent.find_all("a")
			for hyperLink in hyperLinks:
				result.append(hyperLink.string.lower())

	# remove duplicate elements
	result = list(set(result))

	# remove index hyperlinks
	result = [genre for genre in result if genre[0].isalpha()]

	result.sort()

	return result

def groupNumByGenre(groups, genre):
	result = 0

	for (name, url) in groups:
		genres = getGenresList(url)
		if genre in genres:
			result += 1

	return result

def groupNumByGenres(groups, genre1, genre2):
	result = 0

	for (name, url) in groups:
		genres = getGenresList(url)
		if (genre1 in genres) and (genre2 in genres):
			result += 1

	return result

# main program

# initialize pprint
pp = pprint.PrettyPrinter()

URL = "wiki/Category:Alternative_rock_groups_from_Leeds"

# get the groups
groups = getGroupList(URL)

genre1 = 'alternative rock'
genre2 = 'math rock'

a = groupNumByGenre(groups, genre1)
b = groupNumByGenre(groups, genre2)
c = groupNumByGenres(groups, genre1, genre2)

# we use the Jaccard similarity index as a measure of semantic similarity
# for genres A and B we use the following formula:
#     J(A,B) = |A∩B| / |A∪B| = |C| / (|A|+|B|-|C|)
# where |A| and |B| are the number of groups that list A or B as their genre, respectively,
# and |C| is the number of groups that list both A and B

print()
print(f'semantic similarity between "{genre1}" and "{genre2}" genres is {c / (a + b -c)}')
