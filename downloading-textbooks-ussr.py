import os
import re
import requests
from tqdm import tqdm
from bs4 import BeautifulSoup
from urllib.parse import urlencode


class USSRTextbooks:
    def __init__(self):
        self.start_link = 'https://sovietime.ru/skachat-sovetskie-uchebniki'
        self.clean_list_of_category_links = None
        self.clean_list_of_links_from_categories = None

    """Получение ответа"""

    @staticmethod
    def getting_response(url):
        return requests.get(url).text

    """Получение супа"""

    @staticmethod
    def getting_soup(response):
        return BeautifulSoup(response, 'lxml')

    """Изменение директории для загрузки файлов"""

    @staticmethod
    def change_directory():
        os.mkdir('all_books')
        os.chdir('all_books')
        return 1

    @staticmethod
    def collection_of_links(links):
        clean_links = []
        for link in links:
            clean_links.append('https://sovietime.ru' + link['href'])
        return list(set(clean_links))

    """Загрузка файлов"""

    def downloading_books(self):
        count = 0
        download_url = None
        base_url = 'https://cloud-api.yandex.net/v1/disk/public/resources/download?'
        USSRTextbooks.change_directory()
        for public_key in self.clean_list_of_links_from_categories:
            final_url = base_url + urlencode(dict(public_key=public_key))
            response = requests.get(final_url)
            count = count + 1
            try:
                download_url = response.json()['href']
                filename = download_url.split('&')[1].split('=')[-1]
                download_response = requests.get(download_url)
                with open(filename, 'wb') as f:
                    f.write(download_response.content)
                    with open('downloading.log', 'a') as file:
                        file.write(
                            f'[INFO]  Книга №{count} из {len(self.clean_list_of_links_from_categories)} загружена.' + '\n')
            except:
                with open('../download-error.log', 'a') as f:
                    f.write(f'[ERROR]  {download_url} \n')

    """Получение категорий"""

    def getting_categories(self):
        raw_list_links = []
        links = self.getting_soup(self.getting_response(self.start_link)).find('div', class_='cat-children').findAll(
            'a')
        for link in links:
            raw_list_links.append('https://sovietime.ru' + link['href'])
        self.clean_list_of_category_links = list(set(raw_list_links))
        return 1

    """Получение всех ссылок из категорий"""

    def getting_links_from_categories(self):
        books_link = []
        for link in self.clean_list_of_category_links:
            try:
                ls = self.getting_soup(self.getting_response(link)).find('ul', class_='category-module').findAll('a',
                                                                                                                 class_='mod-articles-category-title')
                links = self.collection_of_links(ls)
                for i in tqdm(links, desc=link.split("/")[-1]):
                    all_a = self.getting_soup(self.getting_response(i)).findAll('a')
                    for a in all_a:
                        try:
                            if re.search('https://yadi.sk', a['href']) or re.search('https://disk.', a['href']):
                                books_link.append(a['href'])
                        except:
                            pass
            except:
                with open('get_link_error.log', 'a') as f:
                    f.write(f'[ERROR]  Что-то со страницей категории {link.split("/")[-1]} не так!' + '\n')
        self.clean_list_of_links_from_categories = list(set(books_link))
        return 1


def main():
    ussr = USSRTextbooks()
    ussr.getting_categories()
    ussr.getting_links_from_categories()
    ussr.downloading_books()


if __name__ == '__main__':
    main()
