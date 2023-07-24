from bs4 import BeautifulSoup
from PIL import Image
import numpy as np

import requests
# import urllib.parse
import os
import glob
# import re
import shutil
import stat
import errno
# import time


def search_manga(title):
    base_url = 'https://ww5.mangakakalot.tv/'
    title = title.replace(' ', '%20')
    search_url = base_url + 'search/' + title

    r = requests.get(search_url)
    soup = BeautifulSoup(r.content, 'html5lib')
    table = soup.find('div', attrs={'class': 'panel_story_list'})

    title_array = []
    list_of_div = table.findAll('div', attrs={'class': 'story_item'})
    if (len(list_of_div) == 0):
        print("there were no search results found.")
        main()

    for div in list_of_div:
        title_info = {}

        base_url = 'https://ww5.mangakakalot.tv/'

        title = div.div.h3.a.text
        title_info['title'] = title

        title_link = div.div.find('h3', attrs={'class': 'story_name'}).a['href']
        title_link = base_url + title_link
        title_info['link'] = title_link
        title_array.append(title_info)  # Get the list of titles

    if (len(title_array) == 1):
        print()
        print('Found {}'.format(title_array[0]['title']))
        return title_array[0]
    else:
        print()
        for i in range(len(title_array)):
            print('[{}] {}'.format(i, title_array[i]['title']))

        print('------------------------------------------------------------')
        print('\nWhat title do you wish to download?')
        user_input = input('Input only one number : ')

        if (user_input.isnumeric() and int(user_input) % 1 == 0 and int(user_input) >= 0 and int(user_input) <= len(title_array) - 1):
            return title_array[int(user_input)]
        else:
            print('\nERROR: Incorrect Input. Back to the start.')
            main()
            return


def find_chapters(link):

    r = requests.get(link)
    soup = BeautifulSoup(r.content, 'html5lib')
    base_url = 'https://ww5.mangakakalot.tv'

    chapter_list = []

    table = soup.find('div', attrs={'class': 'chapter-list'})

    for div in table.findAll('div', attrs={'class': 'row'}):

        chapter_info = {}

        try:
            chapter_name_text = div.span.a['href']
            chapter_number = float(chapter_name_text.split('chapter-')[1])
            chapter_info['chapter'] = chapter_number
            chapter_info['link'] = base_url + div.span.a['href']
            chapter_list.append(chapter_info)

        except ValueError:
            continue

    print()
    print('------------------------------------------------------------')

    chapter_list = sorted(chapter_list, key=lambda i: i['chapter'])
    for i in range(len(chapter_list)):
        print('Chapter {}'.format(chapter_list[i]['chapter']))

    print('------------------------------------------------------------')
    print()

    chapter_to_download = []

    print('Please use decimals as there are half chapters as well')
    print('Select specific chapters by using COMMAS i.e 1.0, 2.0, 5.0')
    print('Select a range of chapters by using using DASH - i.e 1.0 - 14.0')
    print('Type \'ALL\' to download all chapters')
    print()
    user_input = input('What chapters should I download for you?: ')
    print()
    print('------------------------------------------------------------')

    if (user_input.upper() == 'ALL'):
        return chapter_list
    elif ('-' in user_input):
        user_input = user_input.replace(' ', '')
        parse_user_input = user_input.split('-')

        for i in np.arange(float(parse_user_input[0]), float(parse_user_input[1]) + 0.1, 0.1):
            num_index = next((index for (index, d) in enumerate(chapter_list) if d['chapter'] == round(i, 1)), None)

            if num_index is None:
                continue

            chapter_to_download.append(chapter_list[num_index])

        return chapter_to_download

    elif (',' in user_input):
        user_input = user_input.replace(' ', '')
        parse_user_input = user_input.split(',')

        for i in range(len(parse_user_input)):
            num_index = next((index for (index, d) in enumerate(chapter_list) if d['chapter'] == float(parse_user_input[i])), None)

            chapter_to_download.append(chapter_list[num_index])

        return chapter_to_download

    else:
        if (int(float(user_input)) % 1 == 0 and int(float(user_input)) >= int(chapter_list[0]['chapter']) and int(float(user_input)) <= len(chapter_list) - 1):
            num_index = next((index for (index, d) in enumerate(chapter_list) if d['chapter'] == round(float(user_input), 1)), None)

            chapter_to_download.append(chapter_list[num_index])

            return chapter_to_download

        else:
            print("Incorrect Input. Back to start")
            main()

    return chapter_to_download


def remove_readonly(func, path, _):
    os.chmod(path, stat.S_IWRITE)
    func(path)


def download_chapter(chapters, dir, title):

    for i in range(len(chapters)):

        print('Beginning download of chapter {}'.format(chapters[i]['chapter']))

        r = requests.get(chapters[i]['link'])

        soup = BeautifulSoup(r.content, 'html5lib')

        div = soup.find('div', attrs={'class': 'vung-doc'})

        images = []

        for img in div.findAll('img', attrs={'class': 'img-loading'}):
            images.append(img['data-src'])

        # check if there are any images in the chapter
        if (len(images) == 0):
            print('Chapter {} has no images'.format(str(chapters[i]['chapter'])))
            print('------------------------------------------------------------')
            continue

        image_folder_path = os.path.join(dir, 'Chapter_' + str(chapters[i]['chapter']))
        os.mkdir(image_folder_path)

        for j in range(len(images)):

            if (images[j].find('.jpg') != 1):
                # end = images[j].find('.jpg')
                f_ext = '.jpg'

            elif (images[j].find('.png') != 1):
                # end = images[j].find('.png')
                f_ext = '.png'
            else:
                print('------------------------------------------------------------')
                print('Image extension not supported')

            pg_num = (str(j+1))
            res = requests.get(images[j])

            f_name = os.path.join(image_folder_path, pg_num + f_ext)
            file = open(f_name, 'wb')
            file.write(res.content)
            file.close()

        im_paths = []

        for file in sorted(glob.glob(image_folder_path + '/*' + f_ext), key=os.path.getmtime):

            try:
                im = Image.open(file)
                im.convert('RGB')
                im_paths.append(im)

            except IndexError:
                print('Images did not load properly. Website fault.')
                continue

        try:
            im1 = im_paths[0]
            im_paths.pop(0)

            chapter_num = chapters[i]['chapter']
            pdf = os.path.join(dir, 'Chapter_{}.pdf'.format(chapter_num))
            im1.save(pdf, resolution=100.0, save_all=True, append_images=im_paths)

            shutil.rmtree(image_folder_path, onerror=remove_readonly)
            ('------------------------------------------------------------')

        except IndexError:
            continue


def main():
    print('------------------------------------------------------------')
    title = input('Manga to download: ')
    title_info = search_manga(title)  # we're returning the title dictionary {'title' : title, 'link' : 'https://link.com'}

    if (' ' in title_info or '\\' in title_info['title'] or '/' in title_info['title'] or ':' in title_info['title']
        or '*' in title_info['title'] or '?' in title_info['title'] or '"' in title_info['title'] or '<' in title_info['title']
            or '>' in title_info['title'] or '|' in title_info['title']):
        edited_title = title_info['title'].replace('\\', '_').replace('/', '_').replace(':', '_').replace('*', '_').replace
        ('?', '_').replace('"', '_').replace('<', '_').replace('>', '_').replace('|', '_')
    else:
        edited_title = title_info['title']

    cwd = os.getcwd()  # current working folder

    title_dir = os.path.join(cwd, edited_title)  # ...PYT\one piece

    try:
        os.mkdir(title_dir)
    except OSError as exc:
        if exc.errno != errno.EEXIST:
            raise
        pass

    chapter = find_chapters(title_info['link'])

    if (len(chapter) == 0):
        print('No chapters to download')
        return
    elif (len(chapter) > 0):
        download_chapter(chapter, title_dir, edited_title)
    else:
        print("ERROR! Something went wrong.")
    print(chapter)


# 'https://ww5.mangakakalot.tv/' - manga website
if __name__ == '__main__':
    main()
