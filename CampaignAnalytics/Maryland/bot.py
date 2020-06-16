from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from CampaignAnalytics import Crawler, Campaign, Candidate, DATE, MAX_PROCESSES
from multiprocessing import Pool
import requests
import time
import os


# this class does all the web crawling (so we can multiprocess the other ones)
class CampaignCrawler(Crawler):
    def __init__(self):
        options = webdriver.FirefoxOptions()
        options.add_argument('--headless')

        self.directory = f"{os.getcwd()}/Downloads/Maryland"
        try:
            os.mkdir(self.directory)
        except FileExistsError:
            pass

        # make the webdriver
        self.driver = webdriver.Firefox(options=options)
        self.driver.maximize_window()

    # create a function that returns candidates
    def find_candidate(self, name=None, ccf_id=None):
        url = 'https://campaignfinance.maryland.gov/Public/ViewCommiteesMain'

        # get the site
        self.driver.get(url)
        time.sleep(4)

        # click continue
        continue_button = self.driver.find_element_by_xpath('//input[@title="Continue"]')
        continue_button.click()
        time.sleep(4)

        # enter candidate information
        name_box = self.driver.find_element_by_xpath('//input[@id="txtCommitteeName"]')
        if ccf_id:
            input_box = self.driver.find_element_by_xpath('//input[@id="txtCommitteeID"]')
            input_box.send_keys(str(ccf_id))
            input_box.send_keys(Keys.ENTER)
        if name:
            name_box.send_keys(name)
            name_box.send_keys(Keys.ENTER)

        if not (ccf_id or name):
            return "No input data provided"

        time.sleep(6)

        # load up the entire information table
        info_cells = self.driver.find_elements_by_xpath('//div[@id="Grid"]//table//tbody//tr//td')

        # get the ccf ID and link for the campaign
        ccf_id = info_cells[1].text

        candidate_info = info_cells[2].find_element_by_tag_name('a')
        campaign_link = candidate_info.get_attribute('href')

        # get the candidate name
        name = candidate_info.text

        new_candidate = Candidate(name, ccf_id, campaign_link)

        return new_candidate

    # create a function to get the campaign information and add it to the candidate
    def add_candidate_campaigns(self, candidate):
        # get the campaign link
        url = candidate.campaign_link
        self.driver.get(url)

        # get the candidate information table
        table_rows = self.driver.find_elements_by_xpath('//td[@id="tdOfficeSoughtList"]//tbody//tr')

        table_rows = [self.format_row(row) for row in table_rows]

        with Pool(processes=MAX_PROCESSES) as pool:
            # map all the table rows to the campaign datatype and add them to
            candidate_campaigns = pool.map(Campaign, table_rows)

        # add the campaigns to the Candidate datatype (object passed by reference)
        candidate.campaigns.extend(candidate_campaigns)

        # change the candidate name to update from the commitee name
        candidate.name = self.driver.find_elements_by_xpath('//td[@id="CandidateList"]//tbody//tr//td')[0].text.title()

    # create a function that gets a csv associated with the campaign
    def download_campaign_csv(self, campaign):
        csv_file = f"{campaign.jurisdiction}_By_Precinct_{campaign.year}_General.csv"
        download_url = f"https://elections.maryland.gov/elections/{campaign.year}/election_data/{csv_file}"
        path = f"{self.directory}/{csv_file}"

        # check if the file already exists
        files = []
        for (dirpath, dirnames, filenames) in os.walk(self.directory):
            files.extend(filenames)
            break

        if csv_file in files:
            return path
        elif DATE.year == int(campaign.year):
            return None
        else:
            # download it if applicable
            response = requests.get(download_url)

            with open(path, 'wb') as outfile:
                outfile.write(response.content)

        return path
