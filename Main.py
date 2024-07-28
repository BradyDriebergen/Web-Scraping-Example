from bs4 import BeautifulSoup
import requests
from transformers import pipeline
import tkinter as tk

# Summarizer pipeline
summarizer = pipeline('summarization', model="sshleifer/distilbart-cnn-12-6")

def get_weather(lat, long):
    # API to get weather data
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": long,
        "current": ["temperature_2m", "precipitation", "wind_speed_10m"],
	    "hourly": ["precipitation_probability", "cloud_cover"]
    }
    responses = requests.get(url, params=params)
    data = responses.json()

    # Get weather values
    weather = {}
    weather["temperature_2m(F)"] = celcius_to_fahrenheit(data["current"]["temperature_2m"])
    weather["precipitation(mm)"] = data["current"]["precipitation"]
    weather["wind_speed(mph)"] = kilometers_to_miles(data["current"]["wind_speed_10m"])
    weather["precipitation_probability(%)"] = data["hourly"]["precipitation_probability"][-1]
    weather["cloud_cover(%)"] = data["hourly"]["cloud_cover"][-1]

    return weather

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

def celcius_to_fahrenheit(celcius):
    return round((celcius * 9/5) + 32, 1)

def kilometers_to_miles(kilometers):
    return round(kilometers * 0.621371, 1)

def print_news(data):
    for key, value in data.items():
        print("Title: " + key)
        print("Summary:" + value + "\n")

def print_weather(weather):
    for key, value in weather.items():
        print(key + ": " + str(value))

def create_window():
    window = tk.Tk()
    window.title("Web Scraping Project")
    window.geometry("800x600")

    news = get_news()
    weather = get_weather(43.618881, -116.215019)

    news_frame = tk.Frame(window)
    news_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    weather_frame = tk.Frame(window)
    weather_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

    for key, value in news.items():
        news_label = tk.Label(news_frame, text="Title: " + key + "\nSummary: " + value, wraplength=800)
        news_label.pack()

    for key, value in weather.items():
        weather_label = tk.Label(weather_frame, text=key + ": " + str(value))
        weather_label.pack()

    window.mainloop()

create_window()