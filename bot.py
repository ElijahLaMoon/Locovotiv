from selenium import webdriver
from multiprocessing import Pool
import time
import os

MAX_PROCESSES = os.cpu_count() * 2


# create a class about campaigns
class Campaign:
    def __init__(self, table_row):
        # use operations on the table row to get the campaign information
        self.year = table_row[0]
        self.election_type = table_row[1]
        self.office_type = table_row[2]
        self.office_sought = table_row[3]
        self.jurisdiction = table_row[4]
        self.party_affiliation = table_row[5]
        self.participation_frequency = table_row[6]
        self.start_date = table_row[7]

    def __repr__(self):
        return f"{self.year} {self.office_sought} ({self.jurisdiction})"


# create a candidate class to store candidate information
class Candidate:
    def __init__(self, name, ccf_id, campaign_link):
        self.name = name
        self.ccf_id = ccf_id
        self.campaign_link = campaign_link

        self.campaigns = []


# this class does all the web crawling (so we can multiprocess the other ones)
class CampaignCrawler:
    def __init__(self):
        options = webdriver.FirefoxOptions()
        options.add_argument('--headless')

        self.directory = f"{os.getcwd()}/Downloads"
        try:
            os.mkdir(self.directory)
        except FileExistsError:
            pass

        profile = webdriver.FirefoxProfile()
        profile.set_preference("browser.download.folderList", 2)
        profile.set_preference("browser.download.manager.showWhenStarting", False)
        profile.set_preference("browser.download.dir", self.directory)

        # make the webdriver
        self.driver = webdriver.Firefox(options=options, profile=profile)
        self.driver.maximize_window()

    # create a function that returns candidates
    def find_candidate(self, name=None, ccf_id=None):
        url = 'https://campaignfinance.maryland.gov/Public/ViewCommiteesMain'

        # get the site
        self.driver.get(url)
        time.sleep(2)

        # click continue
        continue_button = self.driver.find_element_by_xpath('//input[@title="Continue"]')
        continue_button.click()
        time.sleep(2)

        # enter candidate information
        if ccf_id:
            ccf_box = self.driver.find_element_by_xpath('//input[@id="txtCommitteeID"]')
            ccf_box.send_keys(ccf_id)
        if name:
            name_box = self.driver.find_element_by_xpath('//input[@id="txtCommitteeName"]')
            name_box.send_keys(name)

        if not (ccf_id or name):
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

    # create a function that gets a csv associated with the campaign
    def download_campaign_csv(self, campaign):
        csv_file = f"{campaign.jurisdiction}_By_Precinct_{campaign.year}_General.csv"
        download_url = f"https://elections.maryland.gov/elections/2018/election_data/{csv_file}"

        # check if the file already exists
        files = []
        for (dirpath, dirnames, filenames) in os.walk(self.directory):
            files.extend(filenames)
            break

        if csv_file in files:
            return
        else:
            # download it if applicable
            self.driver.get(download_url)

    # create a function that formats table rows
    def format_row(self, row):
        row_list = [cell.text for cell in row.find_elements_by_tag_name('td')]

        return row_list

    def quit(self):
        self.driver.quit()
