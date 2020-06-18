from CampaignAnalytics import DataManager, AnalysisExporter
from difflib import get_close_matches
import pandas as pd
import numpy as np
import os


# create a class that handles all the office data automatically (splits it correctly)
class OfficeFrame(AnalysisExporter):
    def __init__(self, office_name, year, full_df):
        # remember the office name and year
        self.office_name = office_name
        self.year = year

        # split the columns of df
        columns = list(full_df.columns)

        # find the column corresponding to the office name
        start_col = columns.index(office_name)

        # find the ending column
        end_col = self.find_end_col(start_col, columns)

        self.office_df = full_df.iloc[:, start_col:end_col + 1]

        # set the correct headers for the dataframe
        self.candidates = list(self.office_df.iloc[0])
        self.office_df = self.office_df[2:]  # not using the total votes row
        self.office_df.columns = self.candidates

    def find_end_col(self, start_col_index, column_list):
        count = start_col_index
        # iterate through the column list starting at the start index
        for column in column_list[start_col_index + 1:]:
            if 'unnamed' in column.lower():
                count += 1
            else:
                break

        return count

    # do analysis on the dataframe for a specific candidate
    def export_candidate_data(self, inputted_candidate):
        # get the closest matching candidate
        closest_candidate = get_close_matches(inputted_candidate, self.candidates)[0]

        # get the candidate votes column
        votes_for = np.array(self.office_df[closest_candidate]).astype(int)

        # get the total votes
        voting_cols = [np.array(self.office_df[candidate]).astype(int) for candidate in self.candidates]

        # add the votes together
        total_votes = np.array([0 for i in votes_for])
        for col in voting_cols:
            total_votes += col

        precincts = np.array(self.office_df.index)

        output_df = self.sort_df_by_precinct(precincts, votes_for, total_votes, closest_candidate, self.year)

        # send it to a csv

        # make a directory if applicable
        directory = f"{os.getcwd()}/{closest_candidate}"
        try:
            os.mkdir(directory)
        except FileExistsError:
            pass

        # write the csv
        filename = f"{self.office_name} {self.year}.csv".replace('/', ' ')
        output_path = f"{directory}/{filename}"
        output_df.to_csv(output_path, index=False)

    def __repr__(self):
        return f"{self.office_name} ({self.year}) - {self.candidates}"


# create an object that manages the data from a file
class CampaignAnalyzer(DataManager):
    def __init__(self, filename):
        self.filename = filename

        self.office_df = self.setup_df(pd.read_csv(filename))

        # set the index for all of them as the precinct
        precinct_column = list(self.office_df.columns)[1]

        self.office_df = self.office_df.set_index(precinct_column)

        # get all the offices (for later)
        self.office_list = list(self.office_df.columns)

    # create a function that gets the correct office --> create an office frame to compare candidates
    def get_office_data(self, office_name):
        closest_name = get_close_matches(office_name, self.office_list)[0]

        # get the office frame for it
        year = self.filename.split('/')[-1][:4]  # year is always the first 4 digits
        office_frame = OfficeFrame(closest_name, year, self.office_df)

        return office_frame


'''
'''
