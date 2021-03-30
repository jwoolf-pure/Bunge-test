from lib.return_yaml import read_settings
from lib.arrayreport import ArrayReport
from lib.arrayreport import write_array_data
from lib.arrayreport import write_hgroup_data
from lib.arrayreport import write_vgroup_vol_data
from lib.arrayreport import write_exec_data
from lib.arrayreport import calculate_exec_report
from lib.arrayreport import get_dates
from lib.arrayreport import find_first_of_next_month
from lib.charts import add_array_chart
from lib.charts import add_hgroup_chart
from lib.charts import add_hgroup_vol_size_chart
from lib.charts import add_hgroup_vol_snapshot_chart
from lib.charts import add_exec_chart
from lib.logging import setup_logging
from lib.send_mail import send_mail
import argparse
from argparse import RawTextHelpFormatter
from datetime import datetime, timedelta
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
            #print(json.dumps(result, indent=4))

            short_list = []
            dates = get_dates()
            for date in dates:
                found = False
                for item in result:
                    try:
                        time = datetime.strptime(item['time'], '%Y-%m-%dT%H:%M:%SZ')
                        ctime = time.strftime('%m/%d/%Y')
                        comp_time = time.strftime('%b %d, %Y')

                        # Add 80% series
                        item['alert'] = item['capacity'] * .8
                    except:
                        pass
                    if ctime == date:
                        found = True
                        item['time'] = comp_time
                        short_list.append(item)
                if not found:
                    if datetime.now().strftime('%m/%d/%Y') == date:
                        delta = timedelta(days=1)
                        ndate = datetime.now() - delta
                        ndate = ndate.strftime('%m/%d/%Y')
                        for item in result:
                            try:
                                time = datetime.strptime(item['time'], '%Y-%m-%dT%H:%M:%SZ')
                                ctime = time.strftime('%m/%d/%Y')
                                comp_time = time.strftime('%b %d, %Y')

                                # Add 80% series
                                item['alert'] = item['capacity'] * .8
                            except:
                                pass
                            if ctime == ndate:
                                found = True
                                item['time'] = comp_time
                                short_list.append(item)
                                break
                        break


                    time = datetime.strptime(date, '%m/%d/%Y')
                    comp_time = time.strftime('%b %d, %Y')
                    short_list.append({
                        'time': comp_time,
                        'hostname': arrRep.name,
                        'provisioned': 0,
                        'snapshots': 0,
                        'total': 0,
                        'capacity': 0,
                        'alert': 0
                    })

            #print(json.dumps(short_list, indent=4))
            #print(dates)


            sheet_name = arrRep.name
            worksheet = self.workbook.add_worksheet(sheet_name)
            ret = write_array_data(self.workbook, worksheet, short_list)
            self.array_ranges[sheet_name] = ret


    def initialize_array_report(self):
        self.arr_report = []
        for array in self.arrays:
            arrayReport = ArrayReport(array['address'], array['token'], array['name'])
            self.arr_report.append(arrayReport)

    def close_workbook(self):
        self.logger.info("Closing Workbook")
        self.workbook.close()

    def add_executive_sheet_text_data(self):
        self.exec_sheet.set_column(11,11,90)
        blue_fg = self.workbook.add_format()
        red_fg = self.workbook.add_format()
        green_fg = self.workbook.add_format()
        blue_fg.set_font_color('blue')
        red_fg.set_font_color('red')
        green_fg.set_font_color('green')

        self.exec_output_sheet.write(3, 11, 'Total used after optimization - Used storage per application after compression and deduplication is applied.', blue_fg)
        self.exec_output_sheet.write(4, 11, 'Snapshots - Total storage used for snapshots of application volumes (used for quick recovery and DR)', red_fg)
        self.exec_output_sheet.write(5, 11, 'Total Provisioned - Total requested space per application by owners', green_fg)

        self.exec_output_sheet.write(7, 11, 'Local Snapshot Schedule')
        self.exec_output_sheet.write(8, 11, 'Create a snapshot on source every 1 hours')
        self.exec_output_sheet.write(9, 11, 'Retain all snapshots on source for 1 days')
        self.exec_output_sheet.write(10, 11, 'Then retain 4 snapshots per day for 7 more days')

        self.exec_output_sheet.write(12, 11, 'Replication Snapshot Schedule')
        self.exec_output_sheet.write(13, 11, 'Replicate a snapshot to targets every 5 minutes')
        self.exec_output_sheet.write(14, 11, 'Retain all snapshots on targets for 2 hours')
        self.exec_output_sheet.write(15, 11, 'Then retain 4 snapshots per day for 2 more days')



    def add_array_sheet_text_data(self):
        self.array_sheet.set_column(11,11,90)
        blue_fg = self.workbook.add_format()
        red_fg = self.workbook.add_format()
        green_fg = self.workbook.add_format()
        magenta_fg = self.workbook.add_format()
        purple_fg = self.workbook.add_format()
        blue_fg.set_font_color('blue')
        red_fg.set_font_color('red')
        green_fg.set_font_color('green')
        magenta_fg.set_font_color('magenta')
        purple_fg.set_font_color('purple')

        self.array_sheet.write(3, 11, 'Total used after optimization - Used storage including snapshots after compression and deduplication is applied.', red_fg)
        self.array_sheet.write(4, 11, 'Snapshots - Total storage used for snapshots of application volumes (used for quick recovery and DR)', green_fg)
        self.array_sheet.write(5, 11, 'Total Provisioned - Total requested space per application by owners', blue_fg)
        self.array_sheet.write(6, 11, 'Capacity - Total Capacity of the Array', magenta_fg)
        self.array_sheet.write(7, 11, 'Recommended usage limit - 80% of Total Capacity', purple_fg)

        self.array_sheet.write(9, 11, 'Local Snapshot Schedule')
        self.array_sheet.write(10, 11, 'Create a snapshot on source every 1 hours')
        self.array_sheet.write(11, 11, 'Retain all snapshots on source for 1 days')
        self.array_sheet.write(12, 11, 'then retain 4 snapshots per day for 7 more days')

        self.array_sheet.write(14, 11, 'Replication Snapshot Schedule')
        self.array_sheet.write(15, 11, 'Replicate a snapshot to targets every 5 minutes')
        self.array_sheet.write(16, 11, 'Retain all snapshots on targets for 2 hours')
        self.array_sheet.write(17, 11, 'then retain 4 snapshots per day for 2 more days')




    def return_arrays_ranges(self):
        return self.array_ranges

    def return_group_ranges(self):
        return self.hgroup_ranges

    def create_group_sheets(self):
        self.logger.info("Creating Host Group Data Sheets")

        for arrRep in self.arr_report:
            arrRep.calc_hgroups()

            for group in arrRep.calculated_vgroups:
                sheet_name = arrRep.name[0] + arrRep.name[-1] + '_' + group
                if len(sheet_name) > 31:
                    self.logger.warning("Worksheet named: " + sheet_name + " is too long.  Must be less than 31 chars.")
                    continue
                if len(arrRep.calculated_vgroups[group]) == 0:
                    self.logger.warning("No volumes for " + group)
                    continue
                worksheet = self.workbook.add_worksheet(sheet_name)

                self.logger.info("Writing Host Group Data for: " + group)
                ret = write_hgroup_data(self.workbook, worksheet, arrRep.calculated_vgroups[group])
                self.hgroup_ranges[sheet_name] = ret

                self.logger.info("Writing Host Group Volume Data for: " + group)
                ret_group_vols = arrRep.build_series_data(group)
                ret = write_vgroup_vol_data(self.workbook, worksheet, ret_group_vols)
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
            return None
        for group in self.exec_ranges:
            self.logger.info("Adding Executive Chart for: " + group)
            title = "Summary " + group
            exec_chart = add_exec_chart(self.workbook, 'Executive Data', self.exec_ranges[group], title)
            if not exec_chart:
                self.logger.warning("Null return from add_exec_chart.")
                continue
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
    handler.add_array_sheet_text_data()
    handler.create_group_sheets()
    handler.add_hgroup_charts()
    handler.create_exec_sheets()
    handler.add_exec_charts()
    handler.add_executive_sheet_text_data()
    handler.close_workbook()

    if args.email:
        email_users = args.email.split(',')
        send_mail(email_from, email_users, email_subject, email_text,
                  files=[args.file], server=email_relay)

