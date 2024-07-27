from bs4 import BeautifulSoup
import requests
from transformers import pipeline

# Summarizer pipeline
summarizer = pipeline('summarization', model="sshleifer/distilbart-cnn-12-6")

def get_news():
    # Website to scrape
    url = "https://idahonews.com/"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    data = {}
    links = []

    # Get the main headline and other headlines links
    main_headline = soup.find(class_="index-module_teaser__fbfM")
    links.append(url + main_headline.find('a').get('href'))

    other_headlines = soup.find(class_="heroLayout-module_right__kGNn")
    for link in other_headlines.find_all('a')[1:7:2]:
        links.append(url + link.get('href'))

    # loop through the links and get the article text
    for link in links:
        # Get the article text
        temp_response = requests.get(link)
        temp_soup = BeautifulSoup(temp_response.content, 'html.parser')
        temp_section = temp_soup.find(class_="StoryText-module_storyText__FWhP")

        url_text = ""
        for text in temp_section.find_all('p'):
            if (url_text + text.get_text()).__len__() > 1024:
                break
            url_text += text.get_text() + " "
        
        # Summarize the article using AI
        summaryList = summarizer(url_text, max_length=130, min_length=30, do_sample=False)
        summary = str(summaryList[0]['summary_text']).replace(" .", ".")
        data[temp_soup.find('h1', class_="index-module_storyHeadlineText__X9VP").get_text()] = summary

    return data

def print_news(data):
    for key, value in data.items():
        print("Title: " + key)
        print("Summary:" + value + "\n")


data = get_news()
print_news(data)
