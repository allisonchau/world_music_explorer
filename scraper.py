'''This script contains functions to scrape certain sites for artists to feed into caller.py

artists_wikipedia(year)
    gives a sorted list of artists that released an album in the given 'year' parameter.


'''
import pandas as pd

from bs4 import BeautifulSoup
import requests
import html5lib
import fuzzywuzzy

def get_soup(url):
    response = requests.get(url) 
    soup = None
    if response.status_code == 200:
        page = response.text
        soup = BeautifulSoup(page, 'html5lib')
    else:
        print 'Unresponsive. Trying Again...'
        time.sleep(0.5)
        return get_soup(url)
    return soup

def wiki_yearly_albums(year):
    soup = get_soup('https://en.wikipedia.org/wiki/List_of_%d_albums' % (year))
    tables = soup.find_all('table', attrs={'wikitable'})
    df = pd.DataFrame()
    for table in tables:
        date = ' '.join(table.find('td').text.splitlines())
        header = False
        for tr in table('tr'):
            
            first = tr.find('td')
            text = first.text.splitlines() if (first is not None) else 'heading'
            if text is not 'heading':
                row = []
                if len(text) == 2:
                    date = ' '.join(text)
                    row.append(date)
                    for cell in tr.find_all('td'):
                        if ' '.join(cell.text.splitlines())!=date:
                            row.append(cell.text)
                else:
                    row.append(date)
                    for cell in tr.find_all('td'):
                        row.append(cell.text)
                
                if len(row)==7:
                    row.pop()
                    df = df.append(pd.Series(row),ignore_index=True)
    return df

def artists_wikipedia(year):
    return sorted(set(wiki_yearly_albums(year)[1]))


def country_adjectives():
    soup = get_soup('https://en.wikipedia.org/wiki/List_of_adjectival_and_demonymic_forms_for_countries_and_nations')
    table = soup.find('table')
    countries={}
    rows = table.find_all('tr')
    for row in rows:
        if row.find('td')!= None:
            cells = row.find_all('td')
            country = []
            name = cells[0].text.split('[')[0].split('(')[0].replace('"','')
            for i in range(1,len(cells)):
                if cells[i] != None:
                    norm = cells[i].text.split('[')[0].split('(')[0].replace('"','').split(',')
                    for n in norm:
                        slash = len(n.split('/')) != 1
                        wordor = len(n.split(' or '))!=1
                        if (not slash) and (not wordor):
                            country.append(n)
                        elif slash and wordor:
                            for p in n.split('/'):
                                for m in p.split(' or '):
                                    country.append(m)
                        elif slash:
                            for p in n.split('/'):
                                country.append(p)
                        elif wordor:
                            for p in n.split(' or '):
                                country.append(p)
            countries[name] = country
    return countries
def putumayo_page(url):
    soup = get_soup(url)
    table = soup.find('table')
    df = pd.DataFrame()
    rows = table.find_all('tr')
    cols=[]
    for row in rows:
        empt = row.find('td').text
#         print isinstance(row.find('td').text,unicode)
        if empt == u'\xa0' or empt == '' or empt == ' ' or empt =='\t':
            cells = row.find_all('td')
            cols = [c.text for c in cells]
        else:
            cells = row.find_all('td')
            df = df.append(pd.Series([c.text for c in cells]), ignore_index=True)

    df.columns = cols
    putumayo = {a:c for (a, c) in zip(df['ARTIST'],df['COUNTRY'])}
    nexturl = soup.find("div", { "class" : "nav-prev fl" }).a.get('href')

    return (putumayo, nexturl)
    
    
def putumayo_artists(start_url,pages):
    putumayo = {}
    url = start_url
    for i in range(pages):
        try:
            result = putumayo_page(url)
            putumayo.update(result[0])

            url=result[1]
        except:
#             print 'round ',i
            print url

    return putumayo
