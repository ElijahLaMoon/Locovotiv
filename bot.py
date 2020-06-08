from selenium import webdriver
import time

class CampaignCrawler:
    def __init__(self):
        options = webdriver.ChromeOptions()
        # options.add_argument('--headless')

        # make the webdriver
        self.driver = webdriver.Chrome(options=options)
        self.driver.maximize_window()

    def

