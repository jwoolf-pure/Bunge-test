from lib.return_yaml import read_settings
from lib.arrayreport import ArrayReport
from lib.arrayreport import write_array_data
from lib.arrayreport import write_hgroup_data
from lib.charts import add_array_chart
from lib.charts import add_hgroup_chart
from lib.logging import setup_logging
import xlsxwriter

settings = read_settings('settings.yml')


class ArrayHandler:

    def __init__(self):
        self.arrays = settings.get('ARRAYS', None)
        self.array_ranges = {}
        self.hgroup_ranges = {}
        self.workbook = xlsxwriter.Workbook('spreadsheet1.xlsx')
        self.logger = setup_logging('.', 'DEBUG', 'DEBUG')


    def create_chart_sheets(self):
        self.logger.info("Creating Chart Sheets")

        self.array_sheet = self.workbook.add_worksheet('Array_Chart_Sheet')
        self.hgroup_sheet = self.workbook.add_worksheet('Host_Group_Chart_Sheet')

    def create_array_sheets(self):
        self.logger.info("Creating Array Data Sheets")
        for array in self.arrays:
            self.logger.info("Building data for storage array: " + str(array))

            client = ArrayReport(array['address'], array['token'])
            result = client.return_array_space('1y')
            sheet_name = array['name'] + '-' + 'totals'
            worksheet = self.workbook.add_worksheet(sheet_name)
            ret = write_array_data(self.workbook, worksheet, result)
            self.array_ranges[sheet_name] = ret

    def close_workbook(self):
        self.logger.info("Closing Workbook")
        self.workbook.close()

    def return_arrays_ranges(self):
        return self.array_ranges

    def return_group_ranges(self):
        return self.hgroup_ranges

    def create_group_sheets(self):
        self.logger.info("Creating Host Group Data Sheets")

        for array in self.arrays:
            client = ArrayReport(array['address'], array['token'])
            client.calc_hgroups()

            for group in client.calculated_hgroups:
                sheet_name = array['name'] + '_' + group + '_' + 'data'
                worksheet = self.workbook.add_worksheet(sheet_name)
                ret = write_hgroup_data(self.workbook, worksheet, client.calculated_hgroups[group])
                self.hgroup_ranges[sheet_name] = ret

    def add_array_charts(self):
        self.logger.info("Adding Array Charts to Worksheets")

        #array_sheet = self.workbook.add_worksheet('Array_Chart_Sheet')

        row = 3
        for sheet in self.array_ranges:
            array_chart = add_array_chart(self.workbook, sheet, self.array_ranges[sheet])
            cell = 'B' + str(row)
            self.array_sheet.insert_chart(cell, array_chart)
            row += 20


    def add_hgroup_charts(self):
        self.logger.info("Adding Host Group Charts to Worksheets")

        # hgroup_sheet = self.workbook.add_worksheet('Host_Group_Chart_Sheet')

        row = 3
        for sheet in self.hgroup_ranges:
            hgroup_chart = add_hgroup_chart(self.workbook, sheet, self.hgroup_ranges[sheet])
            cell = 'B' + str(row)
            self.hgroup_sheet.insert_chart(cell, hgroup_chart)
            row += 20


def main():
    handler = ArrayHandler()
    handler.create_chart_sheets()
    handler.create_array_sheets()
    handler.add_array_charts()
    handler.create_group_sheets()
    handler.add_hgroup_charts()
    handler.close_workbook()

