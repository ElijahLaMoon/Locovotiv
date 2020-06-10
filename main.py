from bot import CampaignCrawler
from analytics import DataManager
import time
import sys

TARGET_COUNTY = 'Montgomery'

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
        candidate.campaigns.remove(campaign)

# download all the data for the files --> store filepaths
filepaths = [crawler.download_campaign_csv(campaign) for campaign in candidate.campaigns]

# return the nonetype
if None in filepaths:
    filepaths.remove(None)

crawler.quit()

# now for the sorting --> make some managers
start = time.time()

managers = [DataManager(path) for path in filepaths]

# make the csvs --> make a folder and export
count = 0
for manager in managers:
    campaign = candidate.campaigns[count]

    manager.sort_and_export(campaign.office_sought, candidate.name)
    count += 1


end = time.time()

print(f'It took {end - start} seconds to create analytics CSVs.')

'''
NOTES
- test ccf id: 01008957
'''
