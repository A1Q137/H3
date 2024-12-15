from pymongo import MongoClient
import requests
from bs4 import BeautifulSoup
import json
client = MongoClient("mongodb://localhost:27017/")
db = client["cats_and_quotes_db"]
cats_collection = db["cats"]
authors_collection = db["authors"]
quotes_collection = db["quotes"]

# --------------------- CRUD Операції ---------------------

def create_cat(name, age, features):

    try:
        cat = {"name": name, "age": age, "features": features}
        result = cats_collection.insert_one(cat)
        print(f"Кот доданий з ID: {result.inserted_id}")
    except Exception as e:
        print(f"Помилка: {e}")

def read_all_cats():


    try:
        cats = cats_collection.find()
        for cat in cats:
            print(cat)
    except Exception as e:
        print(f"Помилка: {e}")

def read_cat_by_name(name):

    try:
        cat = cats_collection.find_one({"name": name})
        if cat:
            print(cat)
        else:
            print("Кот із таким ім'ям не знайдений.")
    except Exception as e:
        print(f"Помилка: {e}")

def update_cat_age(name, new_age):

    try:
        result = cats_collection.update_one({"name": name}, {"$set": {"age": new_age}})
        if result.modified_count > 0:
            print("Вік кота оновлено.")
        else:
            print("Кот із таким ім'ям не знайдений.")
    except Exception as e:
        print(f"Помилка: {e}")

def add_feature_to_cat(name, feature):


    try:
        result = cats_collection.update_one({"name": name}, {"$push": {"features": feature}})
        if result.modified_count > 0:
            print("Характеристика додана.")
        else:
            print("Кот із таким ім'ям не знайдений.")
    except Exception as e:
        print(f"Помилка: {e}")


def delete_cat_by_name(name):


    try:
        result = cats_collection.delete_one({"name": name})
        if result.deleted_count > 0:
            print("Кот видалений.")
        else:
            print("Кот із таким ім'ям не знайдений.")
    except Exception as e:
        print(f"Помилка: {e}")

def delete_all_cats():

    try:
        cats_collection.delete_many({})
        print("Усі записи видалені.")
    except Exception as e:
        print(f"Помилка: {e}")

# ------------------- Скрапінг та імпорт -------------------

def scrape_quotes():

    base_url = "http://quotes.toscrape.com"
    authors = {}
    quotes = []

    page = 1
    while True:
        response = requests.get(f"{base_url}/page/{page}/")
        if response.status_code != 200:
            break

        soup = BeautifulSoup(response.text, "html.parser")
        quotes_elements = soup.select(".quote")

        for quote in quotes_elements:
            text = quote.find("span", class_="text").get_text(strip=True)
            author = quote.find("small", class_="author").get_text(strip=True)
            tags = [tag.get_text(strip=True) for tag in quote.select(".tags .tag")]

            quotes.append({"tags": tags, "author": author, "quote": text})

            if author not in authors:
                author_link = base_url + quote.find("a")["href"]
                author_response = requests.get(author_link)
                author_soup = BeautifulSoup(author_response.text, "html.parser")

                born_date = author_soup.find(class_="author-born-date").get_text(strip=True)
                born_location = author_soup.find(class_="author-born-location").get_text(strip=True)
                description = author_soup.find(class_="author-description").get_text(strip=True)

                authors[author] = {
                    "fullname": author,
                    "born_date": born_date,
                    "born_location": born_location,
                    "description": description
                }

        page += 1

    with open("quotes.json", "w", encoding="utf-8") as q_file:
        json.dump(quotes, q_file, ensure_ascii=False, indent=4)

    with open("authors.json", "w", encoding="utf-8") as a_file:
        json.dump(list(authors.values()), a_file, ensure_ascii=False, indent=4)

    print("Дані збережені в quotes.json і authors.json.")

    try:
        quotes_collection.insert_many(quotes)
        authors_collection.insert_many(list(authors.values()))
        print("Дані імпортовані в MongoDB.")
    except Exception as e:
        print(f"Помилка при імпорті даних: {e}")

# ------------------- Основне меню -------------------

if __name__ == "__main__":
    while True:
        print("\nОберіть дію:")
        print("1. Додати кота")
        print("2. Переглянути всіх котів")
        print("3. Знайти кота за ім'ям")
        print("4. Оновити вік кота")
        print("5. Додати характеристику коту")
        print("6. Видалити кота за ім'ям")
        print("7. Видалити всіх котів")
        print("8. Зібрати цитати та авторів")
        print("9. Вийти")

        choice = input("Введіть номер дії: ")
        if choice == "1":
            name = input("Введіть ім'я кота: ")
            age = int(input("Введіть вік кота: "))
            features = input("Введіть характеристики через кому: ").split(", ")
            create_cat(name, age, features)
        elif choice == "2":
            read_all_cats()
        elif choice == "3":
            name = input("Введіть ім'я кота: ")
            read_cat_by_name(name)
        elif choice == "4":
            name = input("Введіть ім'я кота: ")
            new_age = int(input("Введіть новий вік кота: "))
            update_cat_age(name, new_age)
        elif choice == "5":
            name = input("Введіть ім'я кота: ")
            feature = input("Введіть нову характеристику: ")
            add_feature_to_cat(name, feature)
        elif choice == "6":
            name = input("Введіть ім'я кота: ")
            delete_cat_by_name(name)
        elif choice == "7":
            delete_all_cats()
        elif choice == "8":
            scrape_quotes()
        elif choice == "9":
            print("Вихід із програми.")
            break
        else:
            print("Невірний вибір. Спробуйте ще раз.")
