from bs4 import BeautifulSoup as bs
import os
import uuid
import glob
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from InfoarenaScrapper import InfoarenaScrapper as isc
"""
MAIN_URL = "https://www.infoarena.ro"
PROBLEMS_URL = "https://www.infoarena.ro/arhiva"
SOLUTIONS_URL = "https://infoarena.ro/monitor?task="
# get data from these source code link
THRESHOLD = 400

options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--incognito')
options.add_argument('--headless')

chrome_driver_location = os.path.dirname(__file__) + "/chrome_driver/chromedriver.exe"
# open up the chrome browser in incognito without opening a window

driver = webdriver.Chrome(executable_path=chrome_driver_location, options=options)

interest_tags = ["cpp", "cpp-32", "cpp-64"]

for file_name in glob.glob("./input_data/code_links_*.*"):

    with open(file_name) as of:
        line_file = of.readline()
        while line_file:
            current_page_url = MAIN_URL + line_file
            driver.delete_all_cookies()
            driver.get(current_page_url)

            current_page_soup = bs(driver.page_source, 'lxml')

            table = current_page_soup.find("div", class_="hljs-ln-line")
            print(table)

            WebDriverWait(driver, 10)

            submit_button = driver.find_element_by_css_selector('#force_view_source').submit()

            WebDriverWait(driver, 10)

            try:
                element = WebDriverWait(driver, 10).until(EC.invisibility_of_element_located((
                    By.ID, 'force_view_source')))
            except:
                pass

            current_page_soup = bs(driver.page_source, 'lxml')
            print(driver.page_source)
            code_used = current_page_soup.find('td', class_='compiler-id').getText()
            table = current_page_soup.find("div", class_="hljs-ln-line")
            print(table)

            # code for extracting the cpp program
            line_file = of.readline()
            break
        break

"""


def get_problems_links(threshold, output_file):
    THRESHOLD = threshold
    PROBLEMS_URL = "https://www.infoarena.ro/arhiva"
    MAIN_URL = "https://www.infoarena.ro"
    # setting up the webdriver
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--incognito')
    options.add_argument('--headless')

    main_directory = os.path.dirname(__file__)
    chrome_driver_location = main_directory + "/chrome_driver/chromedriver.exe"
    # open up the chrome browser in incognito without opening a window
    driver = webdriver.Chrome(executable_path=chrome_driver_location, options=options)
    driver.get(PROBLEMS_URL)
    ranking_dict = {}

    current_page_soup = bs(driver.page_source, 'lxml')
    next_pages_links = current_page_soup.find_all('a', href=True)

    last_page_no = 0
    for href in reversed(next_pages_links):
        if href.getText().isnumeric():
            last_page_no = int(href.getText())
            break

    # iterate through the pages !! here
    # click the button twice to sort the problems
    next_page = 1
    while next_page < last_page_no:
        button_sort_table = driver.find_elements_by_class_name("new_feature")
        if button_sort_table[0].is_displayed():
            driver.execute_script("arguments[0].click()", button_sort_table[0])
            driver.execute_script("arguments[0].click()", button_sort_table[0])

        odd_rows_content = current_page_soup.find_all('tr', class_="odd")
        even_rows_content = current_page_soup.find_all('tr', class_="even")

        # problem solved: get the author href link if one problem has 2-3 authors.
        for odd_row in odd_rows_content:
            no_solutions = odd_row.find('td', class_="").getText()
            href_links = odd_row.select('.task a')
            if int(no_solutions) >= THRESHOLD:
                link = href_links[0]['href']
                ranking_dict[link] = no_solutions
        for even_row in even_rows_content:
            no_solutions = even_row.find('td', class_="").getText()
            href_links = even_row.select('.task a')
            if int(no_solutions) >= THRESHOLD:
                link = href_links[0]['href']
                ranking_dict[link] = no_solutions
        # get the link to the next page
        next_pages_links = current_page_soup.find_all('a', href=True)
        next_page_url = ""
        next_page = next_page + 1
        for href in reversed(next_pages_links):
            if href.getText().isnumeric():
                if int(href.getText()) == next_page:
                    print(next_page)
                    next_page_url = MAIN_URL + href['href']
                    print(next_page_url)
                    break
        driver.get(next_page_url)
        current_page_soup = bs(driver.page_source, 'lxml')

    ranking_sorted = sorted(ranking_dict.items(), key=lambda x: x[1], reverse=True)

    print(len(ranking_dict))

    links_splited = []
    for it in ranking_sorted:
        links_splited.append(it[0].split("/"))
    with open(output_file, 'w') as of:
        for it in links_splited:
            of.write(it[2])
            of.write("\n")
        of.close()

# isc.get_problems_links(400, "problems.data")


def collect_sourcecode_urls(input_file):
    SOLUTIONS_URL = "https://infoarena.ro/monitor?task="
    MAIN_URL = "https://www.infoarena.ro"

    problems_id = []
    with open(input_file, 'r') as opened_file:
        for line in opened_file:
            problems_id.append(line.strip())
        opened_file.close()

    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--incognito')
    options.add_argument('--headless')

    main_directory = os.path.dirname(__file__)
    chrome_driver_location = main_directory + "/chrome_driver/chromedriver.exe"
    # open up the chrome browser in incognito without opening a window
    driver = webdriver.Chrome(executable_path=chrome_driver_location, options=options)

    for problem in problems_id:
        os.chdir(main_directory + "/input_data")
        source_code_links_file = "code_links_" + problem + ".data"
        if problem:
            problem_url = SOLUTIONS_URL + problem

            driver.get(problem_url)

            current_page_soup = bs(driver.page_source, 'lxml')
            next_pages_links = current_page_soup.find_all('a', href=True)

            last_page_no = -1
            for href in reversed(next_pages_links):
                if href.getText().isnumeric():
                    last_page_no = int(href.getText())
                    break

            with open(source_code_links_file, "w") as opened_file:
                counter_solutions = 0
                next_page_no = 1
                while counter_solutions <= 250 and next_page_no <= last_page_no:
                    current_page_soup = bs(driver.page_source, 'lxml')
                    odd_rows_content = current_page_soup.find_all('tr', class_="odd")
                    even_rows_content = current_page_soup.find_all('tr', class_="even")
                    next_page_no = next_page_no + 1
                    for odd_row in odd_rows_content:
                        try:
                            text_extracted = odd_row.find('span', class_="job-status-done").getText()
                        except:
                            break

                        splitted_text = text_extracted.split(' ')

                        if len(splitted_text) == 4:
                            if int(splitted_text[2]) == 100:
                                href_links = odd_row.select('td a', href=True)

                                opened_file.write(href_links[5]['href'] + "\n")

                                counter_solutions = counter_solutions + 1

                    for even_row in even_rows_content:
                        try:
                            text_extracted = even_row.find('span', class_="job-status-done").getText()
                        except:
                            break

                        splitted_text = text_extracted.split(' ')
                        if len(splitted_text) == 4:
                            if int(splitted_text[2]) == 100:
                                href_links = even_row.select('td a', href=True)

                                opened_file.write(href_links[5]['href'] + "\n")

                                counter_solutions = counter_solutions + 1
                    next_pages_links = current_page_soup.find_all('a', href=True)
                    next_page_url = ""
                    for href in next_pages_links:
                        if href.getText() == str(next_page_no):
                            next_page_url = MAIN_URL + href['href']
                            break
                    driver.get(next_page_url)
                    print(next_page_url)
    os.chdir(main_directory)

# isc.collect_sourcecode_url("problems.data")

