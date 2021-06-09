from bs4 import BeautifulSoup
from PIL import Image

import numpy as np

import requests
import urllib.parse
import os
import glob
import re
import shutil
import stat
import errno
import time

from requests.api import request

def search_manga(title):
    base_url = 'http://mangadex.link/'

    title = title.replace(' ', '+') #changing the space on the search to match the website: i.e. tokyo+ghoul
    search_url = base_url + 'search?s=' + title
    r = requests.get(search_url) #get the complete url

    soup = BeautifulSoup(r.content, 'html5lib')

    table = soup.find('div', attrs={'class':'comics-grid'})

    # [ {title: 'name', link: 'https://link.com'}, {}, {} ]
    title_array = []

    list_of_div = table.findAll('div', attrs={'class': 'content'})

    #if there's no table
    if (len(list_of_div) == 0):
        print("...There were no search results found.")
        print()
        exit()

    for div in list_of_div:
        title_info = {}

        title = div.h3.a.text
        title_info['title'] = title
        title_info['link'] = div.h3.a['href']

        title_array.append(title_info)

    if (len(title_array) == 1): #if there's only 1 result
        print('Found {}'.format(title_array[0]['title']))
        print('------------------------------------------------------------')
        return title_array[0]

    else:
        print()
        print('------------------------------------------------------------')
        for i in range(len(title_array)):
            print('[{}] {}'.format(i, title_array[i]['title']))

        print('------------------------------------------------------------')
        print()
        print('What title should I download for you?')
        user_input = input('Input only one number: ')

        if (user_input.isnumeric() and int(user_input) % 1 == 0 and int(user_input) >= 0 and int(user_input) <= len(title_array) - 1):
            return title_array[int(user_input)]
        else:
            print()
            print('ERROR: Incorrect Input. Back to the start.')
            main()
            return


def find_chapters(link):

    r = requests.get(link)

    soup = BeautifulSoup(r.content, 'html5lib')
    chapter_list = []

    #aux to get the manga name
    table_aux = soup.find('div', attrs={'class', 'comic-info'})
    list_of_div_aux = table_aux.findAll('div', attrs={'info'})
    for div in list_of_div_aux:
        a = div.h1.text
        title_aux = a.replace('Manga', '')
        print()
        print (title_aux)


    #to get the manga chapters and it's numbers
    table = soup.find('div', attrs={'class': 'section-body'})
    list_of_div = table.findAll('div', attrs={'class': 'two-rows go-border'})
    print()
    for div in list_of_div:
        chapter_info = {}
        string = div.div.a.strong.text
        string = string.replace(title_aux + 'Chapter', '') #aux to remove the title + manga from the text

        try:
            chapter_number = float(string)
            chapter_info['chapter'] = chapter_number
            chapter_info['link'] = div.div.a['href']
            chapter_list.append(chapter_info)
        
        except ValueError:
            continue
        
    chapter_list = sorted(chapter_list, key=lambda i: i['chapter'])
        
    for i in range(len(chapter_list)):
        print('Chapter {}'.format(chapter_list[i]['chapter']))

    print('------------------------------------------------------------')
    print()


    chapter_to_download = []

    print('Please use decimals as there are half chapters as well') #143.5, 144.0
    print('Choose manga chapters to download sparated by commas i.e 1.0, 2.0, 5.0')
    print('Choose manga chapters by range. USING DASH - i.e 1.0 - 14.0')
    print('Type \'ALL\' to download all chapters')
    print()
    user_input = input('What chapters should I download for you?: ')

    if(user_input.upper() == 'ALL'):
        return chapter_list

    elif('-' in user_input):
        user_input = user_input.replace(' ', '')
        parse_user_input = user_input.split('-') #[5.0, 14.0]

        for i in np.arange(float(parse_user_input[0]), float(parse_user_input[1]) + 0.1, 0.1):
            num_index = next((index for (index,d) in enumerate(chapter_list) if d['chapter'] == round(i,1)), None)

            if(num_index == None):
                continue

            chapter_to_download.append(chapter_list[num_index])

        return chapter_to_download

    elif (',' in user_input):
        user_input = user_input.replace(' ', '')
        parse_user_input = user_input.split(',') #[5.0, 14.0]

        for i in range(len(parse_user_input)):
            num_index = next((index for (index, d) in enumerate(chapter_list) if d['chapter'] == float(parse_user_input[i])), None)

            chapter_to_download.append(chapter_list[num_index])

        return chapter_to_download
    
    #single chapter download
    else:
        if (int(float(user_input)) % 1 == 0 and int(float(user_input)) >= int(chapter_list[0]['chapter']) and int(float(user_input)) <= len(chapter_list) - 1):
            num_index = next((index for (index, d) in enumerate(chapter_list) if d['chapter'] == round(float(user_input), 1)), None)
            
            chapter_to_download.append(chapter_list[num_index])

            return chapter_to_download

        else:
            print("Incorrect Input. Back to start")
            main()

    return chapter_to_download



def download_chapter(chapters, dir, title):

    for i in range(len(chapters)):
        headers = {
            'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36 Edg/91.0.864.41'
            }

        print('... Beginning to download chapter {}'.format(chapters[i]['chapter']))
        print()

        r = requests.get(chapters[i]['link'])
        #print(r)
        
        soup = BeautifulSoup(r.content, 'html5lib')

        div = soup.find('div', attrs={'class':'container-chap'})
        images = div.p.text
        images = images.split(',')
        #print (images)

        
        if (len(images) == 0):
            print('Chapter {} is empty'.format(str(chapters[i]['chapter'])))
            print('------------------------------------------------------------')
            continue

        image_folder_path = os.path.join(dir, 'Chapter ' + str(chapters[i]['chapter']))
        os.mkdir(image_folder_path)

        for j in range(len(images)):
        
            if(images[j].find('.jpg') != 1):
                end = images[j].find('.jpg')
                f_ext = '.jpg'

            elif(images[j].find('.png') != 1):
                end = images[j].find('.png')
                f_ext = '.png'
            else:
                print('------------------------------------------------------------')
                print('Image extension not supported')

            pg_num = (str(j+1))
            res = requests.get(images[j], headers=headers)

            f_name = os.path.join(image_folder_path, pg_num + f_ext)
            file = open(f_name, 'wb')
            file.write(res.content)
            file.close()



def main():
    print()
    print('======= hey hey =======')
    title = input("Wich manga you want to download?: ")

    title_info = search_manga(title) #we're returning the title dictionary {'title' : title, 'link' : 'https://link.com'}

    if('\\' in title_info['title'] or '/' in title_info['title'] or ':' in title_info['title'] or '*' in title_info['title'] 
    or '?' in title_info['title'] or '"' in title_info['title'] or '<' in title_info['title'] or '>' in title_info['title'] or '|' in title_info['title']):
        edited_title = title_info['title'].replace('\\', '_').replace('/', '_').replace(':', '_').replace('*', '_').replace('?', '_').replace('"', '_').replace('<', '_').replace('>', '_').replace('|', '_')
    else:
        edited_title = title_info['title']

    
    cwd = os.getcwd() #get current directory - C:\Users\Bruno\Desktop\Prog\PY\MangaFinal

    title_dir = os.path.join(cwd, edited_title) #tokyo ghoul -> C:\Users\Bruno\Desktop\Prog\PY\MangaFinal\tokyo ghoul

    try:
        os.mkdir(title_dir)
    except OSError as exc:
        if exc.errno != errno.EEXIST:
            raise
        pass


    chapter = find_chapters(title_info['link'])

    if(len(chapter) == 0):
        print('No chapters to download')
        return
    elif (len(chapter) > 0):
        download_chapter(chapter, title_dir, edited_title)
    else:
        print("ERROR!!")


#http://mangadex.link/
if __name__ == '__main__':
    main()
