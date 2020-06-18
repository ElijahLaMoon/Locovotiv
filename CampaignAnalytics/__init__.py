from datetime import datetime as dt
import pandas as pd
import requests
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

    def download_file(self, download_url, path):
        response = requests.get(download_url)

        with open(path, 'wb') as outfile:
            outfile.write(response.content)

    def quit(self):
        self.driver.quit()


# create a base class for analytics to build off of
class DataManager:
    def filter_records(self, column, value, filtering_df=pd.DataFrame()):
        # check if the user reset the filtering df (default to the master)
        if filtering_df.empty:
            filtering_df = self.master_df

        valid_rows = filtering_df[column] == value

        applicable_df = filtering_df[valid_rows]

        return applicable_df

    def export_master(self, column, value):
        # make a directory for the value (usually a name)
        new_directory = f"{os.getcwd()}/{value}"
        try:
            os.mkdir(new_directory)
        except FileExistsError:
            pass

        # overwrite the existing file no matter what
        new_filepath = f"{new_directory}/({value}) {self.filename}"
        new_df = self.filter_records(column, value)
        new_df.to_csv(new_filepath, index=False)

    # create a function that converts xl files to csvs (will not delete old by default)
    def xl_to_csv(self, excel_file, sheet_index=0, delete_old=False):
        df = pd.read_excel(excel_file, sheet_name=sheet_index)
        print(f"Sheet index: {sheet_index}")

        # make it a csv
        path = f"{excel_file.split('.')[0]}.csv"
        df.to_csv(path, index=False)

        # delete the old file if applicable
        if delete_old:
            os.remove(excel_file)

        # return the new filepath
        return path
