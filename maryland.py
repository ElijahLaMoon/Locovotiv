from CampaignAnalytics.Maryland.bot import CampaignCrawler
from CampaignAnalytics.analytics import DataManager
from datetime import datetime as dt
import time
import sys

start = time.time()
TARGET_COUNTY = sys.argv[2]
DATE = dt.now()

user_input = sys.argv[1]
ccf_id = True

try:
    user_input = int(user_input)
except ValueError:
    ccf_id = False

# initialize the crawler
crawler = CampaignCrawler()

# run it
if ccf_id:
    candidate = crawler.find_candidate(ccf_id=user_input)
else:
    candidate = crawler.find_candidate(name=user_input)

# get the campaign information
crawler.add_candidate_campaigns(candidate)

# remove campaigns that are not part of the target county (for now, it's just montgomery county)
temp_campaign_list = candidate.campaigns
for campaign in temp_campaign_list:
    if TARGET_COUNTY != campaign.jurisdiction:
        campaign.jurisdiction = TARGET_COUNTY


# download all the data for the files --> store filepaths
filepaths = [crawler.download_campaign_csv(campaign) for campaign in candidate.campaigns]

# return the nonetype --> only happens for current year
if None in filepaths:
    filepaths.remove(None)

crawler.quit()

# now for the sorting --> make some managers
lap = time.time()

managers = [DataManager(path) for path in filepaths]

# make the csvs --> make a folder and export
count = 0

# make sure the campaigns start at the right date
temp_campaign_list = candidate.campaigns
for campaign in temp_campaign_list:
    if int(campaign.year) == int(DATE.year):
        candidate.campaigns.remove(campaign)

for manager in managers:
    campaign = candidate.campaigns[count]

    manager.sort_and_export(campaign.office_sought, candidate.name, campaign.year)
    count += 1


end = time.time()
print(f"It took {round(lap - start, 2)} seconds to crawl sites.")
print(f'It took {round(end - lap, 2)} seconds to create analytics CSVs.')
print(f"It took {round(end - start, 2)} seconds to perform the entire process.")

'''
NOTES
- test ccf id: 01008957
'''
