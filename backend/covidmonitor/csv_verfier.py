import datetime


def confirm_columns(df, columns):
    if all(x in df.columns.tolist() for x in columns):
        return True
    return False


class Verifier:
    TIME_SERIES_COLUMNS = [["Province/State", "Country/Region"], ["Province_State", "Country_Region"]]
    DAILY_REPORTS_COLUMNS = ["Province_State", "Country_Region", "Confirmed", "Deaths", "Recovered", "Active"]
    SERIES_OPTS = ["deaths", "confirmed", "active", "recovered"]

    SERIES_TYPE_ONE = 1
    SERIES_TYPE_TWO = 2
    DAILY_TYPE_ONE = 3
    DAILY_TYPE_TWO = 4

    def time_series_type(self, file_name):
        lower_file = file_name.lower()
        if "confirmed" in lower_file:
            return "confirmed"
        elif "deaths" in lower_file:
            return "deaths"
        elif "recovered" in lower_file:
            return "recovered"
        elif "active" in lower_file:
            return "active"
        else:
            return -1

    def confirm_valid_csv(self, file_name, df):
        # We first check if we have a daily or time series file
        try:
            datetime.datetime.strptime(file_name, "%m-%d-%Y").date()
            is_daily_file = True
        except ValueError:
            is_daily_file = False
        if is_daily_file and confirm_columns(df, self.DAILY_REPORTS_COLUMNS):
            try:
                datetime.datetime.strptime(file_name, "%m-%d-%Y")
                if df.columns.tolist()[10] == "Combined_Key":
                    return self.DAILY_TYPE_TWO
                return self.DAILY_TYPE_ONE
            except ValueError:
                return -1
            return DAILY
        elif not is_daily_file and confirm_columns(df, self.TIME_SERIES_COLUMNS[0]) and \
                self.time_series_type(file_name) != -1:
            try:
                datetime.datetime.strptime(df.columns.tolist()[5], "%m/%d/%y")
                return self.SERIES_TYPE_ONE
            except ValueError:
                return -1
        elif not is_daily_file and confirm_columns(df, self.TIME_SERIES_COLUMNS[1]) and \
                self.time_series_type(file_name) != -1:
            try:
                datetime.datetime.strptime(df.columns.tolist()[12], "%m/%d/%y")
                return self.SERIES_TYPE_TWO
            except ValueError:
                return -1
        else:  # csv is not valid
            return -1
