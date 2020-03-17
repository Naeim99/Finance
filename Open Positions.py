from bs4 import BeautifulSoup
from urllib.request import urlopen
from selenium import webdriver


# Waymo extract using BeautifulSoup
waymo = 'https://waymo.com/joinus/'
w_html = urlopen(waymo).read()
urlopen(waymo).close()

w_page = BeautifulSoup(w_html, "html.parser")
w_positions = w_page.findAll("li", {"ng-if": "ctrl.categoryIsActive('Finance, Business Systems and REWS', ['Mountain View, California, United States',])"})

n = 0
for w in w_positions:
    title = w.findAll("div", {"class": "careers__roles__roles__role__title__role"})
    location = w.findAll("div", {"class": "careers__roles__roles__role__title__location"})
    while n < len(title):
        title_n = title[n].text.strip()
        location_n = location[n].text.strip()
        print("Waymo:   " + title_n + "   ;   " + location_n)
        n = n + 1

# Varily Extract using Selenium
driver = webdriver.Chrome()
driver.set_page_load_timeout(100)

driver.get("https://verily.com/roles/")
driver.find_elements_by_class_name("job-board-listing-dept")
group = driver.find_element_by_xpath("""//*[@id="job-board-listing"]/li[1]""")
title = group.find_elements_by_class_name("job-title-text")

n = 0
for t in title:
    while n < len(title):
        title_n = title[n].text.strip()
        print("Verily:   " + title_n)
        n = n + 1

driver.close()
