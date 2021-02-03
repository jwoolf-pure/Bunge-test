from lib.return_yaml import read_settings
from lib.arrayreport import ArrayReport
from lib.arrayreport import write_array_data
from lib.arrayreport import write_hgroup_data
from lib.arrayreport import write_hgroup_vol_data
from lib.charts import add_array_chart
from lib.charts import add_hgroup_chart
from lib.charts import add_hgroup_vol_size_chart
from lib.charts import add_hgroup_vol_snapshot_chart
from lib.logging import setup_logging
from lib.send_mail import send_mail
import xlsxwriter
import json
import sys

settings = read_settings('settings.yml')


class ArrayHandler:

    def __init__(self, spreadsheet):
        self.arrays = settings.get('ARRAYS', None)
        self.array_ranges = {}
        self.hgroup_ranges = {}
        self.hgroup_vol_ranges = {}
        self.workbook = xlsxwriter.Workbook(spreadsheet)
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
            sheet_name = array['name']
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
                sheet_name = array['name'] + '_' + group
                worksheet = self.workbook.add_worksheet(sheet_name)

                self.logger.info("Writing Host Group Data for: " + group)
                ret = write_hgroup_data(self.workbook, worksheet, client.calculated_hgroups[group])
                self.hgroup_ranges[sheet_name] = ret

                self.logger.info("Writing Host Group Volume Data for: " + group)
                ret_group_vols = client.build_series_data(group)
                ret = write_hgroup_vol_data(self.workbook, worksheet, ret_group_vols)
                self.hgroup_vol_ranges[sheet_name] = ret

    def add_array_charts(self):
        self.logger.info("Adding Array Charts to Worksheets")

        row = 3
        for sheet in self.array_ranges:
            self.logger.info("Adding Array Charts for: " + sheet)
            array_chart = add_array_chart(self.workbook, sheet, self.array_ranges[sheet], sheet + " Total")
            cell = 'B' + str(row)
            self.array_sheet.insert_chart(cell, array_chart)
            row += 20

    def add_hgroup_charts(self):
        self.logger.info("Adding Host Group Charts to Worksheets")

        row = 3
        for sheet in self.hgroup_ranges:
            self.logger.info("Adding Host Group Chart for: " + sheet)
            hgroup_chart = add_hgroup_chart(self.workbook, sheet, self.hgroup_ranges[sheet], sheet + " Host Group")
            cell = 'B' + str(row)
            self.hgroup_sheet.insert_chart(cell, hgroup_chart)

            self.logger.info("Adding Host Group Vol Size Chart for: " + sheet)
            cell = 'L' + str(row)
            hgroup_vol_chart = add_hgroup_vol_size_chart(self.workbook, sheet, self.hgroup_vol_ranges[sheet], sheet + " Vol Sizes")
            self.hgroup_sheet.insert_chart(cell, hgroup_vol_chart)

            self.logger.info("Adding Host Group Vol Snapshots Chart for: " + sheet)
            cell = 'U' + str(row)
            hgroup_vol_chart = add_hgroup_vol_snapshot_chart(self.workbook, sheet, self.hgroup_vol_ranges[sheet], sheet + " Snapshot Sizes")
            self.hgroup_sheet.insert_chart(cell, hgroup_vol_chart)

            row += 20


def parse_arguments():
    parser = argparse.ArgumentParser(prog='array_annual',
                                     usage='array_annual [options]',
                                     formatter_class=RawTextHelpFormatter)
    parser.add_argument('--email', help='Email report to this address', required=False)
    parser.add_argument('--file', help='File name of the spreadsheet', required=False)
    args = parser.parse_args()
    return args


def main():
    args = parse_arguments()
    handler = ArrayHandler(args.file)
    handler.create_chart_sheets()
    handler.create_array_sheets()
    handler.add_array_charts()
    handler.create_group_sheets()
    handler.add_hgroup_charts()
    handler.close_workbook()

    text = ''' 
    This is the storage array report.
    '''
    if args.email:
        send_mail('jwoolf@purestorage.com', args.email, 'Pure Array Report', text, files=[args.file],
                  server="127.0.0.1")
