from urllib.error import URLError
from urllib.request import urlopen

from bs4 import BeautifulSoup


def weather_station_fetch(url):
    try:
        html = urlopen(url).read()

        soup = BeautifulSoup(html, "html.parser")

        attributes = [
            "Temperatura",
            "Humedad",
            "Punto de rocío",
            "Viento promedio 10min",
            "Presión atmósferica",
        ]

        data = {}
        for attribute in attributes:
            td_text = soup.find(lambda tag: tag.name == 'td' and attribute in tag.get_text())
            td_value = td_text.find_next_sibling("td").get_text()
            print(attribute)
            print(td_value)
            data[attribute] = td_value
            if attribute == "Temperatura":
                val = td_value.split("\u00b0")
                data[attribute] = float(val[0])

            elif attribute == "Humedad":
                data[attribute] = int(td_value[0:2])

            elif attribute == "Punto de rocío":
                val = td_value.split("\u00b0")
                data[attribute] = float(val[0])

            else:
                data[attribute] = td_value
        return data
    except URLError as e:
        print("Error: " + e.reason)


if __name__ == "__main__":
    url = "http://150.214.57.165/meteo/Current_Vantage.htm"
    data = weather_station_fetch(url)
    print(data)
