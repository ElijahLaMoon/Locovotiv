from bot import CampaignCrawler
import sys
import json

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

for campaign in candidate.campaigns:
    print(json.dumps(campaign.__dict__, indent=4))

crawler.quit()

'''
NOTES
- test ccf id: 01008957
'''
