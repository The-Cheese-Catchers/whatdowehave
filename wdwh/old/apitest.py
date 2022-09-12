import requests

if __name__ == "__main__":
    url = "https://api.edamam.com/api/recipes/v2?type=public&q=risotto&app_id=de17dfe1&app_key=3369ce0941f655d0ebbaef9c6ad21815"
    r = requests.get(url)
    data = r.json()
    for i in data:
        print(i)