from bot import CampaignCrawler
import json
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

crawler.quit()

'''
NOTES
- test ccf id: 01008957
'''
