from bs4 import BeautifulSoup
import requests
from transformers import pipeline


summarizer = pipeline('summarization', model="sshleifer/distilbart-cnn-12-6")

url_name = "https://idahonews.com/"
url = requests.get(url_name)
soup = BeautifulSoup(url.content, 'html.parser')

section = soup.find(class_="heroLayout-module_right__kGNn")

for link in section.find_all('a')[1:7:2]:
    temp_url = requests.get(url_name + link.get('href'))
    temp_soup = BeautifulSoup(temp_url.content, 'html.parser')
    temp_section = temp_soup.find(class_="StoryText-module_storyText__FWhP")

    url_text = ""
    for text in temp_section.find_all('p'):
        url_text += text.get_text() + " "
    
    print("Title: " + link.get_text())
    
    summaryList = summarizer(url_text, max_length=130, min_length=30, do_sample=False)
    summary = str(summaryList[0]['summary_text']).replace(" .", ".")
    print("Summary: " + summary + '\n')