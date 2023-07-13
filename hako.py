from bs4 import *
import subprocess
from os import mkdir
from os.path import isdir, exists
import requests
import os

hako_link = "https://docln.net"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.97 Safari/537.36',
    'Referer': 'https://ln.hako.vn/'
}
STORAGE_PATH = "../storage"

session = requests.Session()


def minimize_url(url):
    try:
        if url[len(url) - 1] == '/':
            url = url[:-1]
        return url
    except:
        return url


def get_novel_name(url):
    lists = url.split('/')
    return lists[4]


def get_volume_name(url):
    lists = url.split('/')
    # print(lists)
    return lists[5]
def get_chapter_name(url):
    lists = url.split('/')
    # print(lists)
    name = lists[5]
    try:
        while not name[0] == '-':
            name = name[1:]
        return name
    except:
        return lists[5]

class Novel():
    def __init__(self, url = "", name = "no_name"):
        self.name = name
        self.url = url
        if not url == "":
            self.name = get_novel_name(url)
        self.novel_path = STORAGE_PATH + f"/{self.name}"
        self.list_volumes = self.get_novel_volume()
        if not isdir(self.novel_path):
            mkdir(self.novel_path)
        if not isdir(self.novel_path + "/src"):
            mkdir(self.novel_path + "/src")

    def get_novel_volume(self):
        url = minimize_url(self.url)
        content_html = subprocess.check_output(f'curl {url}')
        soup = BeautifulSoup(content_html, "html.parser")
        contents = soup.find_all('div', class_="volume-cover")
        lists = []
        for content in contents:
            # volume_url = url + "/t" + content['id'][7:]
            for x in BeautifulSoup(str(content), "html.parser").find_all('a', href=True):
                lists.append(hako_link + x['href'])
                # print(x['href'])
        return lists


class Volume():
    def __init__(self, outer, url, name = "no_volume"):
        self.outer = outer
        self.name = name
        self.url = url

        if not url == "":
            self.name = get_volume_name(url)
            # print(self.name)

        self.list_chapters = self.get_volume_chapter()
        self.vol_path = self.outer.novel_path + "/" + self.name
        # print(self.vol_path)

        if not isdir(self.vol_path):
            mkdir(self.vol_path)
        if not isdir(self.vol_path + "/src"):
            mkdir(self.vol_path + "/src")

    def get_volume_chapter(self):
        url = minimize_url(self.url)
        # print(f'curl {url}')
        content_html = subprocess.check_output(f'curl {url}')
        soup = BeautifulSoup(content_html, "html.parser")
        contents = soup.find_all('div', class_ = "chapter-name")
        lists = []
        for content in contents:
            for x in BeautifulSoup(str(content), "html.parser").find_all('a', href=True):
                lists.append(hako_link + x['href'])
        return lists

    def get_chapter_content(self, url, volume_name="-"):
        print("Get chapter:", url)
        content_html = subprocess.check_output(f'curl {url}')
        soup = BeautifulSoup(content_html, "html.parser")

        novel = Novel(url=url)
        chap_name = get_chapter_name(url)
        contents = soup.find_all('p')
        print(self.vol_path)
        file_path = f"{self.vol_path}/{chap_name}.html"
        try:
            with open(file_path, "wb") as file:
                for content in contents:
                    imgs = content.findChildren('img', recursive=False)

                    for img in imgs:
                        try:
                            with open(f"""{volume.vol_path}/src/{img['alt']}""", 'wb') as handler:
                                handler.write(session.get(img['src'], headers=HEADERS).content)
                        except:
                            pass
                        img['src'] = f"""src/{img['alt']}"""
                        file.write(img.prettify("utf-8"))

                        content.clear()

                    file.write(content.prettify("utf-8"))
                    print("Add:", content['id'])
        except:
            print("Có lỗi mẹ nó rồi")

def download_novel(novel_url):
    try:
        novel = Novel(url=novel_url)

        # print(novel.list_volumes)

        for volume_url in novel.list_volumes:
            volume = Volume(outer=novel, url=volume_url)
            # print(volume.url)
            for chapter_url in volume.list_chapters:
                volume.get_chapter_content(url=chapter_url)
        print("done", novel_url)
        return "done!!"
    except:
        print(STORAGE_PATH)
        return "loi"

if __name__ == "__main__":
    pass
    # novel_url = "https://ln.hako.vn/truyen/15210-tensei-saki-wa-jisaku-shousetsu-no-akuyaku-shoukoushaku-deshita-danzai-saretakunai-node-tekitai-kara-dekiai-ni-monogatari-wo-kakikaemasu"
    #
    # download_novel(novel_url)

