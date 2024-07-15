from bs4 import BeautifulSoup
import requests
from colorama import Fore

piratebays_link = "https://1.piratebays.to/s/"


def create_request(page, query, category):
    payloads = {"page": page, "category": category, "q": query}

    request = requests.get(piratebays_link, params=payloads)
    if request.status_code == 200:
        return request.content
    else:
        return None


def get_films_and_pages(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    main_content_div = soup.find("tbody")
    if main_content_div:
        tr_elements = main_content_div.find_all("tr")
        tr_list = [str(tr) for tr in tr_elements]
        return tr_list[:-1], tr_list[-1]
    else:
        return []


def write(text, color):
    print(color + text + Fore.RESET, end="")


movies_html, pages_html = get_films_and_pages(create_request(1, "titanic", 0))


def get_page_count(pages_html):
    soup = BeautifulSoup(pages_html, "html.parser")
    a_elements = soup.find_all("a")
    if a_elements:
        return int(a_elements[-1].get_text())
    else:
        return 0


def parse_movie_html(movie_html):
    soup = BeautifulSoup(movie_html, "html.parser")
    attributes = soup.find_all("td")
    nobr = attributes[3].find("nobr")
    a = nobr.find("a")
    href = a["href"]
    movie_attributes = [attribute.get_text() for attribute in attributes]

    movie = {
        "title": movie_attributes[1].strip("\n"),
        "date": movie_attributes[2].strip("\n"),
        "size": movie_attributes[4].strip("\n"),
        "seeds": movie_attributes[5].strip("\n"),
        "leeches": movie_attributes[6].strip("\n"),
        "user": movie_attributes[7].strip("\n"),
        "link": href.strip("\n"),
    }

    return movie


def get_movies_from_page(movies_html):
    movies = [parse_movie_html(movie) for movie in movies_html]
    return movies


import os


def print_movie(movie):
    write(movie["title"] + " ", Fore.WHITE)
    write(movie["size"] + " ", Fore.GREEN)
    write(movie["seeds"] + " ", Fore.BLUE)
    write(movie["leeches"] + " ", Fore.RED)
    write(movie["date"], Fore.YELLOW)

def play(movie):
    os.system(f"peerflix {movie['link']} --vlc")

while True:
    page = 1
    action = input("Enter action: ")
    if action.startswith("search "):
        movie_name = action[7:]
    elif action.startswith("page "):
        page = int(action[5:])
    elif action.startswith("select "):
        selection = int(action[7:]) - 1
        write(f"{movies[selection]['title']} playing...",Fore.WHITE)
        play(movies[selection])
        break
    elif action == "exit":
        break
    else:
        print("Invalid action.")
        continue

    movies_html, pages_html = get_films_and_pages(create_request(page, movie_name, 0))
    page_count = get_page_count(pages_html)
    movies = get_movies_from_page(movies_html)
    for index, movie in enumerate(movies):
        write(str(index + 1) + ") ", Fore.LIGHTCYAN_EX)
        print_movie(movie)
        print()
    print(f"Page: {page}/{page_count}")
