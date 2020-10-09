from bs4 import BeautifulSoup as bs
from selenium import webdriver
import os

class InfoarenaScrapper:

    MAIN_URL = "https://www.infoarena.ro"
    PROBLEMS_URL = "https://www.infoarena.ro/arhiva"
    SOLUTIONS_URL = "https://infoarena.ro/monitor?task="

    def get_problems_links(self, threshold, output_file):
        THRESHOLD = threshold

        # setting up the webdriver
        options = webdriver.ChromeOptions()
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--incognito')
        options.add_argument('--headless')

        main_directory = os.path.dirname(__file__)
        chrome_driver_location = main_directory + "/chrome_driver/chromedriver.exe"
        # open up the chrome browser in incognito without opening a window
        driver = webdriver.Chrome(executable_path=chrome_driver_location, options=options)
        driver.get(self.PROBLEMS_URL)
        ranking_dict = {}

        current_page_soup = bs(driver.page_source, 'lxml')
        next_pages_links = current_page_soup.find_all('a', href=True)

        last_page_no = ""
        for href in reversed(next_pages_links):
            if href.getText().isnumeric():
                last_page_no = href.getText()
                break

        # iterate through the pages !! here
        # click the button twice to sort the problems
        next_page = 1
        while next_page <= last_page_no:
            next_page = next_page + 1
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
                    ranking_dict.update({link: int(no_solutions)})
                else:
                    break
            for even_row in even_rows_content:
                no_solutions = even_row.find('td', class_="").getText()
                href_links = even_row.select('.task a')
                if int(no_solutions) >= THRESHOLD:
                    link = href_links[0]['href']
                    ranking_dict.update({link: int(no_solutions)})
                else:
                    break
            # get the link to the next page
            next_pages_links = current_page_soup.find_all('a', href=True)
            next_page_url = ""
            for href in next_pages_links:
                if href.getText() == str(next_page):
                    next_page_url = self.MAIN_URL + href['href']
                    break
            driver.get(next_page_url)

        ranking_sorted = sorted(ranking_dict.items(), key=lambda x: x[1], reverse=True)

        links_splited = []
        for it in ranking_sorted:
            links_splited.append(it[0].split("/"))
        with open(output_file, 'w') as of:
            for it in links_splited:
                of.write(it[2])
                of.write("\n")
            of.close()

    def collect_sourcecode_urls(self, input_file):
        problems_id = []

        file_in = input_file
        with open(file_in, 'r') as opened_file:
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
                problem_url = self.SOLUTIONS_URL + problem

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
                                next_page_url = self.MAIN_URL + href['href']
                                break
                        driver.get(next_page_url)
        os.chdir(main_directory)

    def create_hierarchy(self, root_name, problems_names_file, score):
        with open(problems_names_file, 'r') as of:
            for line in of:
                dir_name = root_name + '/' + str(line.strip()) + '/' + score
                try:
                    os.makedirs(dir_name)
                    print("Directory ", dir_name, " Created ")
                except FileExistsError:
                    print("Directory ", dir_name, " already exists")

                if not os.path.exists(dir_name):
                    os.makedirs(dir_name)
                    print("Directory", dir_name, "Created")
                else:
                    print("Directory", dir_name, "already exists")
        of.close()
