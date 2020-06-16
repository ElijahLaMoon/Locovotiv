from datetime import datetime as dt
import os

# add the constants here
MAX_PROCESSES = os.cpu_count() * 2
DATE = dt.now()


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


# create a base class for others to build off
class Crawler:
    # create a function that formats table rows
    def format_row(self, row):
        row_list = [cell.text for cell in row.find_elements_by_tag_name('td')]

        return row_list

    def quit(self):
        self.driver.quit()
