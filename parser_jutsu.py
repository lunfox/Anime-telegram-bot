import random
from bs4 import BeautifulSoup
import requests

class Jutsu:

    def __init__(self):
        self.url = 'https://jut.su'
        self.headers = [
            {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X x.y; rv:42.0) Gecko/20100101 Firefox/42.0'},
            {'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0'}
        ]

    def search(self, name):
        self.html_text = requests.get(self.url + '/' + name, headers=self.headers[random.randint(0, 1)]).text
        self.soup = BeautifulSoup(self.html_text, "html.parser")
        if not self.soup.find('h1', class_='header_video'):
            return False
        else:
            self.name = self.soup.find('h1', class_='header_video').text
        self.data = {}
        for i in self.soup.find_all(class_='short-btn'):
            text = i.text.split()
            for j in range(len(text) - 1):
                if text[j].isnumeric() and text[j + 1] == 'сезон':
                    index = text[j] + ' ' + text[j + 1]
                    if not self.data.get(index):
                        self.data[index] = {}
                    subindex = text[j + 2] + ' ' + text[j + 3]
                    self.data[index][subindex] = i['href']
                    break
                elif text[j].isnumeric() and text[j + 1] == 'фильм':
                    if not self.data.get('Фильмы'):
                        self.data['Фильмы'] = {}
                    subindex = text[j] + ' ' + text[j + 1]
                    self.data['Фильмы'][subindex] = i['href']
                    break
                elif text[j].isnumeric() and text[j + 1] == 'серия':
                    if not self.data.get('Серии'):
                        self.data['Серии'] = {}
                    subindex = text[j] + ' ' + text[j + 1]
                    self.data['Серии'][subindex] = i['href']
                    break
        return True