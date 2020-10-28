from bs4 import BeautifulSoup as bs
from selenium import webdriver
import os
import uuid
import requests
import shutil


class InfoarenaScrapper:

    MAIN_URL = "https://www.infoarena.ro"
    PROBLEMS_URL = "https://www.infoarena.ro/arhiva"
    SOLUTIONS_URL = "https://infoarena.ro/monitor?task="
    ARHIVA_URL = "https://infoarena.ro/arhiva-educationala"

    PROBLEMS_FILENAME = "problems.data"

    def setup_chrome_driver(self):
        main_directory = os.path.dirname(__file__)
        chrome_driver_location = main_directory + "/chrome_driver/chromedriver.exe"
        options = webdriver.ChromeOptions()
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--incognito')
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('log-level=2')

        driver = webdriver.Chrome(executable_path=chrome_driver_location, options=options)

        return driver

    def get_problems_links(self, threshold):

        driver = self.setup_chrome_driver()
        driver.get(self.PROBLEMS_URL)

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
                if int(no_solutions) >= threshold:
                    link = href_links[0]['href']
                    ranking_dict[link] = no_solutions
            for even_row in even_rows_content:
                no_solutions = even_row.find('td', class_="").getText()
                href_links = even_row.select('.task a')
                if int(no_solutions) >= threshold:
                    link = href_links[0]['href']
                    ranking_dict[link] = no_solutions
            # get the link to the next page
            next_pages_links = current_page_soup.find_all('a', href=True)
            next_page_url = ""
            next_page = next_page + 1
            for href in reversed(next_pages_links):
                if href.getText().isnumeric():
                    if int(href.getText()) == next_page:
                        next_page_url = self.MAIN_URL + href['href']
                        break
            driver.get(next_page_url)
            current_page_soup = bs(driver.page_source, 'lxml')

        ranking_sorted = sorted(ranking_dict.items(), key=lambda x: x[1], reverse=True)

        print(len(ranking_dict))

        with open(self.PROBLEMS_FILENAME, 'w') as of:
            for it in ranking_sorted:
                of.write(it[2].split("/")[2])
                of.write("\n")
            of.close()

    def collect_sourcecode_urls(self, input_file, dataset_folder):
        problems_id = []

        with open(input_file, 'r') as opened_file:
            for line in opened_file:
                problems_id.append(line.strip())
            opened_file.close()

        driver = self.setup_chrome_driver()
        max_tries = 3
        for problem in problems_id:
            for current_try in range(0,max_tries):
                try:
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

                                        self.extract_problem(self.MAIN_URL, problem, 100, href_links[5]['href'], dataset_folder)

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

                                        self.extract_problem(self.MAIN_URL, problem, 100, href_links[5]['href'], dataset_folder)

                                        counter_solutions = counter_solutions + 1
                            next_pages_links = current_page_soup.find_all('a', href=True)
                            next_page_url = ""
                            for href in next_pages_links:
                                if href.getText() == str(next_page_no):
                                    next_page_url = self.MAIN_URL + href['href']
                                    break
                            driver.get(next_page_url)
                    break
                except Exception as e:
                    print(f"Exception on {problem_name} at #{current_try + 1} try with exception {e}")
                    if(os.path.exists(f'dataset/{dataset_folder}/{problem_name}')):
                        shutil.rmtree(f'dataset/{dataset_folder}/{problem_name}')

    def extract_problem(self, url_body, problem_name, score, problem_url, dataset_folder):
        interest_tags = ["cpp", "cpp-32", "cpp-64"]
        problem_path = f'dataset/{dataset_folder}/{problem_name}/{score}'
        os.makedirs(problem_path, exist_ok=True)
        url = url_body + problem_url
        problem_id = f'{uuid.uuid1()}.cpp'
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
        max_tries = 3
        for current_try in range(0, max_tries):
            try:
                request = requests.post(url, data={"force_view_source": "Vezi sursa"}, headers = headers)
                current_page_soup = bs(str(request.content), 'lxml')

                code = current_page_soup.find('code')
                compiler = current_page_soup.find('td', class_="compiler-id").getText()
                if compiler in interest_tags:
                    with(open(f'{problem_path}/{problem_id}', "w", encoding="utf-8")) as problem_file:
                        code_text = code.getText()
                        problem_file.write(code_text.encode().decode("unicode_escape"))
                break
            except Exception as e:
                print(f"Exception on solution {problem_url} at #{current_try + 1} try with exception {e}")
                if(os.path.exists(f'{problem_path}/{problem_id}')):
                    os.remove(f'{problem_path}/{problem_id}')

    def collect_urls_arhiva(self, output_file):
        driver = self.setup_chrome_driver()
        driver.get(self.ARHIVA_URL)

        current_page_soup = bs(driver.page_source, 'lxml')

        next_pages_links = current_page_soup.find_all('a', href=True)

        last_page_no = 0
        for href in reversed(next_pages_links):
            if href.getText().isnumeric():
                last_page_no = int(href.getText())
                break
        next_page = 1
        links = []
        while next_page <= last_page_no:
            odd_rows_content = current_page_soup.find_all('tr', class_="odd")
            even_rows_content = current_page_soup.find_all('tr', class_="even")

            for odd_row in odd_rows_content:
                links.append(odd_row.find('a', class_="")['href'])
            for even_row in even_rows_content:
                links.append(even_row.find('a', class_="")['href'])

            next_pages_links = current_page_soup.find_all('a', href=True)
            next_page_url = ""
            next_page = next_page + 1
            for href in reversed(next_pages_links):
                if href.getText().isnumeric():
                    if int(href.getText()) == next_page:
                        next_page_url = self.MAIN_URL + href['href']
                        break
            try:
                driver.get(next_page_url)
                current_page_soup = bs(driver.page_source, 'lxml')
            except:
                break
        with open(output_file, 'w') as of:
            for it in links:
                of.write(it.split("/")[2])
                of.write("\n")
            of.close()
'''
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
'''