import requests
from bs4 import BeautifulSoup
import concurrent.futures
import threading
import sqlite3

thread_local = threading.local()


def get_session():
    if not hasattr(thread_local, "session"):
        thread_local.session = requests.Session()
    return thread_local.session


def download_site(url):
    session = get_session()
    session.verify = False
    with session.get(url) as response:
        soup = BeautifulSoup(response.text, 'html.parser')
        for title in soup.find_all('title'):
            insert_data(title.get_text(), url)


def download_all_links(links):
    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        executor.map(download_site, links)


def insert_data(title, url):
    try:
        conn = sqlite3.connect('db')
        cursor = conn.cursor()
        query = "Insert into records(title, url) values('{0}', '{1}')".format(title, url)
        cursor.execute(query)
        conn.commit()
    except sqlite3.Error as e:
        print(e)


if __name__ == "__main__":
    try:
        url = input('Enter url:')
        request = requests.get(url)
        soup = BeautifulSoup(request.text, 'html.parser')
        urls = []
        for link in soup.find_all('a'):
            urls.append(link.get('href'))
        download_all_links(urls)
    except Exception as e:
        pass

