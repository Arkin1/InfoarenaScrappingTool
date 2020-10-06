class InfoarenaScrapper:

    MAIN_URL = "https://www.infoarena.ro"
    PROBLEMS_URL = "https://www.infoarena.ro/arhiva"
    SOLUTIONS_URL = "https://infoarena.ro/monitor?task="

    def get_problems_links(self, threshold, output_file):
        from bs4 import BeautifulSoup as bs
        from selenium import webdriver
        import os

        NO_PAGES = 44
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
        # iterate through the pages !! here
        # click the button twice to sort the problems
        for page in range(1, NO_PAGES + 1):
            next_page = page + 1
            if next_page > NO_PAGES:
                break
            button_sort_table = driver.find_elements_by_class_name("new_feature")
            if button_sort_table[0].is_displayed():
                driver.execute_script("arguments[0].click()", button_sort_table[0])
                driver.execute_script("arguments[0].click()", button_sort_table[0])

            current_page = bs(driver.page_source, 'lxml')

            odd_rows_content = current_page.find_all('tr', class_="odd")
            even_rows_content = current_page.find_all('tr', class_="even")

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
            next_pages_links = current_page.find_all('a', href=True)
            next_page_url = ""
            for href in next_pages_links:
                if href.getText() == str(next_page):
                    next_page_url = self.MAIN_URL + href['href']
            driver.get(next_page_url)

        ranking_sorted = sorted(ranking_dict.items(), key=lambda x: x[1], reverse=True)

        links_splited = []
        for it in ranking_sorted:
            links_splited.append(it[0].split("/"))
        with open(output_file, 'w') as file:
            for it in links_splited:
                file.write(it[2])
                file.write("\n")

