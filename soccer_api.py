"""
DS3500 HW_03
Author: Ruhan Bhakta
soccer_api.py

API for interacting with the soccer dataset. Used in dashboard.py
"""
import pandas as pd

class SOCCERAPI():
    def __init__(self, filename=None):
        """ Initialize and optionally load data """
        self.data = None
        if filename:
            self.load_data(filename)

    def load_data(self, filename):
        """ Load and store the data """
        self.data = pd.read_csv(filename)
        return self.data

    def get_data(self, min_goals=10, min_assists=0, comp=None, squad=None, age_range=None, min_minutes=0):
        """ Return player data filtered by goals, assists, league, squad, age, and minutes played"""
        # Apply Goals Filter
        filtered = self.data[self.data["Gls"] >= min_goals]
        # Apply Assists filter
        filtered = filtered[filtered["Ast"] >= min_assists]
        # Apply competition filter if provided
        if comp is not None:
            if isinstance(comp, list):
                filtered = filtered[filtered["Comp"].isin(comp)]
            else:
                filtered = filtered[filtered["Comp"] == comp]
        # Apply squad filter if provided
        if squad is not None:
            if isinstance(squad, list):
                filtered = filtered[filtered["Squad"].isin(squad)]
            else:
                filtered = filtered[filtered["Squad"] == squad]
        # Apply age filter if provided
        if age_range is not None:
            filtered = filtered[(filtered['Age'] >= age_range[0]) & (filtered['Age'] <= age_range[1])]
        # Apply minutes filter
        filtered = filtered[filtered["Min"] >= min_minutes]
        return filtered

    def get_unique_values(self, column):
        """ Get sorted unique values for a column """
        return sorted(list(self.data[column].unique()))

    def get_column_range(self, column):
        """ Get min/max range for a column """
        return int(self.data[column].min()), int(self.data[column].max())

    def get_squads_by_competition(self, comp_values):
        """ Get available squads filtered by selected competitions """
        filtered_data = self.data if not comp_values else self.data[self.data['Comp'].isin(comp_values)]
        return sorted(list(filtered_data['Squad'].unique()))

    def get_player_position(self, player_name):
        """ Get position for a specific player """
        player_row = self.data[self.data['Player'] == player_name]
        if not player_row.empty:
            return player_row['Pos'].values[0]
        return None
