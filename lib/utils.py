from lib.return_yaml import read_settings
from lib.arrayreport import ArrayReport
from lib.arrayreport import write_array_data
from lib.arrayreport import write_hgroup_data
from lib.arrayreport import write_hgroup_vol_data
from lib.arrayreport import write_exec_data
from lib.arrayreport import calculate_exec_report
from lib.charts import add_array_chart
from lib.charts import add_hgroup_chart
from lib.charts import add_hgroup_vol_size_chart
from lib.charts import add_hgroup_vol_snapshot_chart
from lib.charts import add_exec_chart
from lib.logging import setup_logging
from lib.send_mail import send_mail
import argparse
from argparse import RawTextHelpFormatter
from datetime import datetime
import xlsxwriter

import json
import sys

settings = read_settings('settings.yml')

email_from = settings.get('EMAIL_FROM', None)
email_relay = settings.get('EMAIL_RELAY', None)
email_subject = settings.get('EMAIL_SUBJECT', None)
email_text = settings.get('EMAIL_TEXT', None)


class ArrayHandler:

    def __init__(self, spreadsheet):
        self.arrays = settings.get('ARRAYS', None)
        self.array_ranges = {}
        self.hgroup_ranges = {}
        self.hgroup_vol_ranges = {}
        self.workbook = xlsxwriter.Workbook(spreadsheet)
        self.logger = setup_logging('./logs', 'DEBUG', 'DEBUG')

    def create_exec_sheets(self):
        self.exec_output = calculate_exec_report(self.arr_report)
        self.exec_sheet = self.workbook.add_worksheet('Executive Data')
        ret = write_exec_data(self.workbook, self.exec_sheet, self.exec_output)
        self.exec_ranges = ret


    def create_chart_sheets(self):
        self.logger.info("Creating Chart Sheets")

        self.exec_output_sheet = self.workbook.add_worksheet('Executive_Report')
        self.array_sheet = self.workbook.add_worksheet('Array_Sheet')
        self.hgroup_sheet = self.workbook.add_worksheet('Host_Group_Sheet')

    def create_array_sheets(self):
        self.logger.info("Creating Array Data Sheets")

        for arrRep in self.arr_report:
            self.logger.info("Building data for storage array: " + str(arrRep.name))

            result = arrRep.return_array_space('1y')
            sheet_name = arrRep.name
            worksheet = self.workbook.add_worksheet(sheet_name)
            ret = write_array_data(self.workbook, worksheet, result)
            self.array_ranges[sheet_name] = ret


    def initialize_array_report(self):
        self.arr_report = []
        for array in self.arrays:
            arrayReport = ArrayReport(array['address'], array['token'], array['name'])
            self.arr_report.append(arrayReport)

    def close_workbook(self):
        self.logger.info("Closing Workbook")
        self.workbook.close()

    def return_arrays_ranges(self):
        return self.array_ranges

    def return_group_ranges(self):
        return self.hgroup_ranges

    def create_group_sheets(self):
        self.logger.info("Creating Host Group Data Sheets")

        for arrRep in self.arr_report:
            arrRep.calc_hgroups()

            for group in arrRep.calculated_hgroups:
                sheet_name = arrRep.name[0] + arrRep.name[-1] + '_' + group
                if len(sheet_name) > 31:
                    self.logger.warning("Worksheet named: " + sheet_name + " is too long.  Must be less than 31 chars.")
                    continue
                worksheet = self.workbook.add_worksheet(sheet_name)

                self.logger.info("Writing Host Group Data for: " + group)
                ret = write_hgroup_data(self.workbook, worksheet, arrRep.calculated_hgroups[group])
                self.hgroup_ranges[sheet_name] = ret

                self.logger.info("Writing Host Group Volume Data for: " + group)
                ret_group_vols = arrRep.build_series_data(group)
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

    def add_exec_charts(self):
        self.logger.info("Adding Executive Charts")

        row = 3
        if self.exec_ranges == None:
            return
        for group in self.exec_ranges:
            self.logger.info("Adding Executive Chart for: " + group)
            title = "Summary " + group
            exec_chart = add_exec_chart(self.workbook, 'Executive Data', self.exec_ranges[group], title)
            cell = 'B' + str(row)
            self.exec_output_sheet.insert_chart(cell, exec_chart)
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
    parser.add_argument('--file', help='File name of the spreadsheet', required=True)
    args = parser.parse_args()
    return args


def main():
    args = parse_arguments()
    handler = ArrayHandler(args.file)
    handler.initialize_array_report()
    handler.create_chart_sheets()
    handler.create_array_sheets()
    handler.add_array_charts()
    handler.create_group_sheets()
    handler.add_hgroup_charts()
    handler.create_exec_sheets()
    handler.add_exec_charts()
    handler.close_workbook()

    if args.email:
        email_users = args.email.split(',')
        send_mail(email_from, email_users, email_subject, email_text,
                  files=[args.file], server=email_relay)
