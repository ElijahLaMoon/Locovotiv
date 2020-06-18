from CampaignAnalytics import Crawler, Candidate, DataManager
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
import pandas as pd
import os
import time

# set the min and max years depending on the
MIN_YEAR = 2014
MAX_YEAR = 2018


# create a campaign crawler that inherits from the OG
class CampaignCrawler(Crawler, DataManager):
    def __init__(self):
        options = webdriver.FirefoxOptions()
        options.add_argument('--headless')

        self.directory = f"{os.getcwd()}/Downloads/Ohio"
        try:
            os.makedirs(self.directory)
        except FileExistsError:
            pass

        # make the webdriver
        self.driver = webdriver.Firefox(options=options)
        self.driver.maximize_window()

        # set a master_df (for default)
        self.link_csv = f"{os.getcwd()}/CampaignAnalytics/Ohio/links.txt"
        self.master_df = pd.read_csv(self.link_csv)

    def find_candidate(self, name=None):
        url = 'https://www6.ohiosos.gov/ords/f?p=CFDISCLOSURE:1:9295067691106::NO::::'

        # get the url
        self.driver.get(url)

        # send the keys and search
        if name:
            candidate_name_box = self.driver.find_element_by_xpath('//input[@id="P1_CANDIDATE"]')
            candidate_name_box.send_keys(name)

        if not name:
            return "No input data provided"

        run_report_button = self.driver.find_element_by_xpath('//button[@value="Run Report"]')
        run_report_button.click()

        time.sleep(4)

        # use the available information to create a candidate object (no ccf id in ohio)
        candidate_information_potentials = self.driver.find_elements_by_xpath('//tr[@class="highlight-row"]')

        count = 0
        for potential in candidate_information_potentials:
            test_activity = potential.text.strip().lower().split(' ')
            test_bool = 'active' in test_activity
            if test_bool:
                candidate_name = self.driver.find_elements_by_xpath('//tr[@class="highlight-row"]//td[@headers="ID_COMB_NAME"]')[count].text
                ccf_id = self.driver.find_elements_by_xpath('//tr[@class="highlight-row"]//td[@headers="EN_PAC_NO"]')[count].text
                campaign_link = self.driver.find_elements_by_xpath('//tr[@class="highlight-row"]//td[@headers="LINK$03"]//a')[count].get_attribute('href')

                new_candidate = Candidate(candidate_name, ccf_id, campaign_link)

                return new_candidate
                break
            count += 1

        # only reaches here if no candidate was found
        return None

    # create a function to add campaign information (only years are available here)
    def get_running_years(self, candidate):
        if not candidate:
            return set()
        url = candidate.campaign_link
        self.driver.get(url)
        time.sleep(5)

        # get the years off the table (full campaign info isn't available)
        years = set()

        # go thru all the pages
        while True:
            try:
                new_years = {int(element.text) for element in self.driver.find_elements_by_xpath('//td[@headers="RP_YEAR"]')}
                years = years | new_years
                next_page_button = self.driver.find_element_by_xpath('//a[@class="sPaginationNext"]')
                next_page_button.click()
                time.sleep(5)
            except NoSuchElementException:
                break

        years = {year for year in years if ((year <= MAX_YEAR) and (year >= MIN_YEAR))}
        return years

    # this gets all the campaign data for a candidate (no years available)
    def download_campaign_data(self, year, office_level):
        # match the data with the current info (see txt file)
        link_df = pd.read_csv(self.link_csv)
        offices_df = self.filter_records('Election Year', year, filtering_df=link_df)

        if not offices_df.empty:
            download_link = list(self.filter_records('Offices', office_level, filtering_df=offices_df)['File Name'])[0]
        else:
            return

        # download the correct year and office
        filename = download_link.split('/')[-1]

        # check if the year is in the filename
        if not (str(year) in filename):
            filename = f"{year}_{filename}"

        path = f"{self.directory}/{filename}"

        # check if the file already exists
        files = os.listdir(self.directory)
        test_file = f"{filename.split('.')[0]}.csv"
        if test_file in files:
            path = f"{self.directory}/{test_file}"
            return path

        self.download_file(download_link, path)

        # convert xl files to csv with pandas (xl takes too much space)
        new_path = self.xl_to_csv(path, sheet_index=1, delete_old=True)  # use the second sheet (master)

        return new_path


'''
NOTES
- test candidate: Andrew Ginther --> can use Ginther Andrew OR Ginther
    - no , in name for this one
'''
