import youtube_dl
from pydub import AudioSegment # use later
import subprocess
import os
from bs4 import BeautifulSoup
import requests 

def link_to_database(link):
    return subprocess.Popen(['youtube-dl', '--extract-audio', '--audio-format', \
                                   'wav', '--output', 'audio/%(id)s.%(ext)s', \
                                   '--postprocessor-args', '-r 4100', link])


def get_fnames():
    """
    returns the list of all filenames in audio
    """

    return os.listdir("audio")

def fname2id(fname):
    """
    get the id from the filename
    """

    return fname.split("/")[:-4]


query_url = "https://www.youtube.com/results?search_query="
watch_url = "https://www.youtube.com/watch?v="

def get_soup_from_url(url):
    try:
        r = requests.get(url,'lxml')
    except:
        r = requests.get(url)
    soup = BeautifulSoup(r.text,'lxml')
    
    return soup


def get_video_from_query(query):
    soup = get_soup_from_url(query)
    section_soup = soup.find("ol",{"class":"item-section"})
    divs_soup = section_soup.findAll("div",{"class":"yt-lockup-video"})
    videos = []
    for s in divs_soup:
        title_soup = s.find("h3",{"class":"yt-lockup-title"})
        title = title_soup.find("a")['title']
        href = title_soup.find("a")['href'] 
        time = s.find("div",{"class":"video-thumb"}).find("span",{"class":"video-time"}).find(text=True)
        publisher = s.find("div",{"class":"yt-lockup-byline"}).find(text=True)
        if href[:6]=="/watch":
            video_id=href[9:]
            videos.append([title,video_id])
    return videos


if __name__ == '__main__':
    n_jobs = 4

    videos = get_video_from_query(query_url + "thelonius+monk")

    nvideos = [v for v in videos if v[1] not in [fname2id(elt) for elt in get_fnames()]]
    videos = nvideos

    process = [link_to_database(watch_url + videos[i][1]) for i in range(max(n_jobs, len(videos)))]

    if len(videos) > n_jobs:
        for i in range(n_jobs, len(videos)):
            waiting = True
            while waiting:
                for j in range(n_jobs):
                    if process[j].poll() is not None:
                        process[j] = link_to_database(watch_url + videos[i][1])
                        waiting = False
                        break

