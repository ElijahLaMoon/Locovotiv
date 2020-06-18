from CampaignAnalytics.Ohio.bot import CampaignCrawler
from CampaignAnalytics.Ohio.analytics import CampaignAnalyzer
from datetime import datetime as dt
import time
import sys

start = time.time()
DATE = dt.now()

# use name, office level, and office
NAME = sys.argv[1].strip().title()
OFFICE_LEVEL = sys.argv[2].strip().title()
OFFICE = sys.argv[3].strip().title()

# create a crawler
crawler = CampaignCrawler()

# find the candidate
candidate = crawler.find_candidate(name=NAME)

# get the running years --> download them
running_years = crawler.get_running_years(candidate)
data_paths = [crawler.download_campaign_data(year, OFFICE_LEVEL) for year in running_years]

crawler.quit()

lap = time.time()

# analyze each data path with a campaign analyzer
analysts = [CampaignAnalyzer(path) for path in data_paths if path]

# get office frames for all of the years --> use OG NAME
office_frames = [analyst.get_office_data(OFFICE_LEVEL) for analyst in analysts]

# export the office frames one by one
for frame in office_frames:
    frame.export_candidate_data(NAME)

end = time.time()

print(f"It took {round(lap - start, 2)} seconds to crawl sites.")
print(f'It took {round(end - lap, 2)} seconds to create analytics CSVs.')
print(f"It took {round(end - start, 2)} seconds to perform the entire process.")
