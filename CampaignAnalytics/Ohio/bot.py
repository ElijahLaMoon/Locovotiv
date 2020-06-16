from CampaignAnalytics import Crawler, Candidate
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
        candidate_information_potentials = self.driver.find_elements_by_xpath('//tr[@class="highlight-row"]')
        candidate_information_raw = None

        for potential in candidate_information_potentials:
            if 'active' in potential.find_element_by_xpath('//td[@headers="STATUS"]').text.lower():
                candidate_information_raw = potential
                break

        if candidate_information_raw:
            candidate_name = candidate_information_raw.find_element_by_xpath('//td[@headers="ID_COMB_NAME"]').text
            ccf_id = candidate_information_raw.find_element_by_xpath('//td[@headers="EN_PAC_NO"]').text
            campaign_link = candidate_information_raw.find_element_by_xpath('//td[@headers="LINK$03"]').text

            new_candidate = Candidate(candidate_name, ccf_id, campaign_link)

            return new_candidate
        else:
            return "No active candidate found"

    # create a function to add campaign information (only years are available here)
    def get_running_years(self, candidate):
        url = candidate.campaign_link
        self.driver.get(url)

        # get the years off the table (full campaign info isn't available)
        years = {element.text for element in self.driver.find_elements_by_xpath('//td[@headers="RP_YEAR"]')}
        return years

    # this gets all the campaign data for a candidate (no years available)
    def download_campaign_data(self, candidate):
        'https://www.sos.state.oh.us/globalassets/elections/2015/general/precinct.xlsx'
        'https://www.sos.state.oh.us/globalassets/elections/2016/gen/precinctlevel.xlsx'
        'https://www.sos.state.oh.us/globalassets/elections/2017/gen/statewideresults-byprecinct.xlsx'
        'https://www.sos.state.oh.us/globalassets/elections/2018/gen/2018-11-06_statewideprecinct.xlsx'

        # convert xl files to csv with pandas (xl takes too much space)


'''
NOTES
- test candidate: Andrew Ginther --> can use Ginther Andrew OR Ginther
    - no , in name for this one
'''
