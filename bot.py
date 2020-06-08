from selenium import webdriver
import time


class CampaignCrawler:
    def __init__(self):
        options = webdriver.ChromeOptions()
        # options.add_argument('--headless')

        # make the webdriver
        self.driver = webdriver.Chrome(options=options)
        self.driver.maximize_window()

    def get_campaign_link(self, name=None, ccf=None):
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
        info_table = self.driver.find_elements_by_xpath('//div[@id="Grid"]//table//tbody//tr')
        top_candidate_info = info_table[0].find_elements_by_xpath('//td')

        # get the ccf ID and link for the campaign
        self.ccf_id = top_candidate_info[1].text

        candidate_info_link = top_candidate_info[2].find_element_by_xpath('//a').get_attribute('href')

        return candidate_info_link
