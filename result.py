# -*- coding: utf-8 -*-
"""
Created on Mon Mar 27 16:10:00 2017

@author: temp
"""

import pandas as pd
from bs4 import BeautifulSoup as bs
import urllib2
import numpy as np
import matplotlib.pyplot as plt
import re

# при первом чтении файла выявляется, что некоторые строки имеют 12 столбцов, а большенство 11
# необходимо поправить таблицу
data = pd.read_csv(r'D:\Projects\yandex_analitic\ufo.csv', names = range(12), na_values = [0,'0','.',''])
bad_rows = data.dropna(axis = 0 , subset=[11])
# видим, что в bad_rows есть лишние столбцы 4-5 и отсутствует столбец duration (seconds)
# поправляем
bad_rows = bad_rows.drop([4],axis=1)
bad_rows = bad_rows[[0,1,2,3,6,5,7,8,9,10,11]] #ставим 5й столбец как duration (seconds)
#читаем исходные даные без bad_rows
data = data.drop(11, axis = 1)
data.columns = data.loc[0,:].values
data = data.drop(0, axis = 0)
                  
#добавляем bad_rows
bad_rows.columns = data.columns.tolist() #переименовывам столбцы bad_rows
data = pd.concat([data, bad_rows])
# убираем строки с nan в графе штат
data = data.dropna(axis = 0, subset =['state'])
#берем из интернета акронимы штатов и их русские названия
response = urllib2.urlopen('https://ru.wikipedia.org/wiki/%D0%A1%D0%BF%D0%B8%D1%81%D0%BE%D0%BA_%D1%88%D1%82%D0%B0%D1%82%D0%BE%D0%B2_%D0%B8_%D1%82%D0%B5%D1%80%D1%80%D0%B8%D1%82%D0%BE%D1%80%D0%B8%D0%B9_%D0%A1%D0%A8%D0%90_%D0%BF%D0%BE_%D1%87%D0%B8%D1%81%D0%BB%D0%B5%D0%BD%D0%BD%D0%BE%D1%81%D1%82%D0%B8_%D0%BD%D0%B0%D1%81%D0%B5%D0%BB%D0%B5%D0%BD%D0%B8%D1%8F')
html = response.read()
states = bs(html, 'html.parser')
table = states.find('table', {'class':'standard sortable'})
table_text = [td for td in table.find_all('td')][:549]
english_acro = [table_text[i].text.lower() for  i in range(3,len(table_text),11)]
russian_name = [table_text[i].text for  i in range(1,len(table_text),11)]
#добавляем названия штатов на русском
wikiData = pd.DataFrame(data={'stateRU': russian_name}, index =english_acro)
data['stateRu'] = [wikiData.stateRU[i] if i in english_acro else None for i in data['state'].values.tolist()]
#берем из data дынные только для штатов
us_data = data.dropna(subset=['stateRu'], axis = 0)
top10states = us_data['state'].value_counts()[:10]
top10statesDf = pd.DataFrame(data ={'state': top10states.index.tolist(), 'Count': top10states.values, 'stateRU': [wikiData.stateRU[i] for i in top10states.index]}, index=top10states.index)
print 'топ-10 штатов США по параметру встречаемости НЛО'
print top10statesDf
## предположим что кол-во свидетельст зависит от плотности населения 
## посчитаем плотность населения
#population = np.array([np.int(table_text[i].contents[1].replace(' ','')) for  i in range(5,len(table_text),11)], np.float32)
#area = np.array([np.int(table_text[i].contents[0].encode('ascii','ignore')) for  i in range(6,len(table_text),11)])
#density = population/area
#wikiData['density'] = density
#top10statesDf['density'] = [wikiData.density[i] for i in top10statesDf.index]
##корреляции нет. 

#отобразим места где встречали НЛО
dataWithCoor = data.dropna(axis = 0, subset = ['latitude', 'longitude'])
#почистим значения полей широты долготы от мусора
dataWithCoor.loc[:,'latitude'] = [np.float32(re.sub('[^0-9.\-]','',str(i))) for i in dataWithCoor.loc[:,'latitude'].values]
dataWithCoor.loc[:,'longitude'] = [np.float32(re.sub('[^0-9.\-]','',str(i))) for i in dataWithCoor.loc[:,'longitude'].values]
plt.plot(dataWithCoor.latitude.values, dataWithCoor.longitude.values,'.')

#import gmap
#
#gmap = gmplot.GoogleMapPlotter(0, 0, 2)
#gmap.heatmap(dataWithCoor.latitude.values, dataWithCoor.longitude.values)
#gmap.draw("mymap.html")