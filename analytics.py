import pandas as pd
import numpy as np
import os


# create a class to organize voting information by precinct
class PrecinctPoll:
    def __init__(self, precinct_df, candidate):
        self.candidate = candidate
        self.precinct = list(precinct_df['Precinct'])[0]

        # calculate the amount of people that voted for the candidate (and didn't)
        candidate_bool = precinct_df['Candidate Name'] == candidate
        candidate_row = precinct_df[candidate_bool]

        # use the first and last names if there is no data in the candidate row
        if len(candidate_row) == 0:
            names = candidate.split(' ')
            simple_name = f"{names[0]} {names[-1]}"
            candidate_bool = precinct_df['Candidate Name'] == simple_name
            candidate_row = precinct_df[candidate_bool]

        self.votes_for = int(candidate_row['Election Night Votes'])

        self.total_votes = sum(precinct_df['Election Night Votes'])

        self.votes_against = self.total_votes - self.votes_for

        try:
            self.percentage_for = self.votes_for / self.total_votes
        except ZeroDivisionError:
            self.percentage_for = 'X'

    def output_row(self):
        row = [self.precinct, self.votes_against, self.votes_for, self.percentage_for]
        return row

    def __repr__(self):
        return f"{self.precinct} {self.candidate} - {round(self.percentage_for * 100)}% ({self.votes_for}/{self.total_votes})"


# create a class that sorts the data
class DataManager:
    def __init__(self, filename):
        self.filename = filename
        self.master_df = pd.read_csv(filename)

        # set up the dataframe correctly
        self.master_df = self.master_df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

        # set up precincts
        counties = np.array(self.master_df['Election District']) * 1000
        precincts = np.array(self.master_df['Election Precinct'])
        precinct_codes = counties + precincts

        self.master_df.drop(columns=['County', 'Election District', 'Election Precinct'], inplace=True)

        # add the precinct data back
        self.master_df = pd.concat([pd.DataFrame(precinct_codes, columns=['Precinct']), self.master_df], axis=1)

    # create a class to get a particular candidate's records

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

    # create a function that returns a dataframe of sorted information
    def sort_file(self, office_name, candidate):
        office_votes_df = self.filter_records('Office Name', office_name)

        # sort the dataframe into precincts
        precincts = list(set(office_votes_df['Precinct']))
        precincts.sort()

        precinct_dfs = [self.filter_records('Precinct', precinct, filtering_df=office_votes_df) for precinct in precincts]

        # create a bunch of precinct poll data types based on the precinct dataframes
        precinct_polls = [PrecinctPoll(df, candidate) for df in precinct_dfs]

        return precinct_polls

    # create a function that outputs the precinct data
    def sort_and_export(self, office_name, candidate, year):
        headers = ['Precinct', f"Opponent {year}", f"{candidate} {year}", f"{candidate} Percentage {year}"]
        precinct_polls = self.sort_file(office_name, candidate)

        # create a folder if necessary
        self.directory = f"{os.getcwd()}/{candidate}"
        try:
            os.mkdir(self.directory)
        except FileExistsError:
            pass

        # format the data into a dataframe
        data = [poll.output_row() for poll in precinct_polls]
        output_df = pd.DataFrame(data, columns=headers)

        # output the dataframe (no matter what --> want it to be most recent)
        output_df.to_csv(f"{self.directory}/{office_name} {year}.csv", index=False)


# create a class that can compare between years


'''
NOTES
- opponent {year} --> just all the people that didnt vote for the candidate
    - this calculates
'''
