from CampaignAnalytics import Crawler, Campaign, Candidate
from selenium import webdriver
import os
import time


# create a campaign crawler that inherits from the OG
class CampaignCrawler(Crawler):
    def __init__(self):
        options = webdriver.FirefoxOptions()
        options.add_argument('--headless')

        self.directory = f"{os.getcwd()}/Downloads/Ohio"
        try:
            os.mkdir(self.directory)
        except FileExistsError:
            pass

        # make the webdriver
        self.driver = webdriver.Firefox(options=options)
        self.driver.maximize_window()

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
        candidate_information_raw = self.driver.find_element_by_xpath('//tr[@class="highlight-row"]')
        candidate_name = candidate_information_raw.find_element_by_xpath('//td[@headers="ID_COMB_NAME"]')
        ccf_id = None
        campaign_link = candidate_information_raw.find_element_by_xpath('//td[@headers="LINK$03"]')

        new_candidate = Candidate(candidate_name, ccf_id, campaign_link)

        return new_candidate


'''
NOTES
- test candidate: CALLENDER, JAMIE --> can use Callender Jamie OR  Callender
    - no , in name for this one
'''
