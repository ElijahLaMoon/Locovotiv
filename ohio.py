from CampaignAnalytics.Ohio.bot import CampaignCrawler
from datetime import datetime as dt
import time
import sys

start = time.time()
DATE = dt.now()
# use name and office level
NAME = sys.argv[1].strip().title()
OFFICE_LEVEL = sys.argv[2].strip().title()

# create a crawler
crawler = CampaignCrawler()

# find the candidate
candidate = crawler.find_candidarte(name=NAME)

# get the running years --> download them
running_years = crawler.get_running_years(candidate)
data_paths = [crawler.download_campaign_data(year, OFFICE_LEVEL) for year in running_years]

# analyze each data path with a campaign analyzer
