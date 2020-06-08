from selenium import webdriver
import time
import os

MAX_PROCESSES = os.cpu_count() * 2


# create a class about campaigns
class Campaign:
    def __init__(self, table_row):
        # use operations on the table row to get the campaign information
        stuff = ''


# create a candidate class to store candidate information
class Candidate:
    def __init__(self, name, ccf_id, campaign_link):
        self.name = name
        self.ccf_id = ccf_id
        self.campaign_link = campaign_link

        self.campaigns = []

    # use the campaign object to add campaigns
    def add_campaign(self, campaign):
        self.campaigns.append(campaign)


# this class does all the web crawling (so we can multiprocess the other ones)
class CampaignCrawler:
    def __init__(self):
        options = webdriver.FirefoxOptions()
        options.add_argument('--headless')

        # make the webdriver
        self.driver = webdriver.Firefox(options=options)
        self.driver.maximize_window()

    # create a function that returns candidates
    def find_candidate(self, name=None, ccf=None):
        url = 'https://campaignfinance.maryland.gov/Public/ViewCommiteesMain'

        # get the site
        self.driver.get(url)
        time.sleep(2)

        # click continue
        continue_button = self.driver.find_element_by_xpath('//input[@title="Continue"]')
        continue_button.click()
        time.sleep(2)

        # enter candidate information
        if ccf:
            ccf_box = self.driver.find_element_by_xpath('//input[@id="txtCommitteeID"]')
            ccf_box.send_keys(ccf)
        if name:
            name_box = self.driver.find_element_by_xpath('//input[@id="txtCommitteeName"]')
            name_box.send_keys(name)

        if not (ccf or name):
            return "No input data provided"

        # click search
        search_button = self.driver.find_element_by_xpath('//input[@id="btnSearch"]')
        search_button.click()
        time.sleep(3)

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

    def quit(self):
        self.driver.quit()
