from purestorage import FlashArray
import urllib3
import logging
from datetime import datetime

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
urllib3_log = logging.getLogger("urllib3")
urllib3_log.setLevel(logging.CRITICAL)
logger = logging.getLogger('array_annual')
import json
import sys

suffixes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']


def humansize(nbytes):
    i = 0
    while nbytes >= 1024 and i < len(suffixes) - 1:
        nbytes /= 1024.
        i += 1
    f = ('%.2f' % nbytes).rstrip('0').rstrip('.')
    return '%s %s' % (f, suffixes[i])


class ArrayReport:

    def __init__(self, address, token, name):
        self.client = FlashArray(address, api_token=token)
        self.name = name

    def return_array_space(self, time):
        return self.client.get(space=True, historical=time)

    def return_host_groups(self):
        return self.client.list_hgroups(connect=True)

    def set_volumes(self):
        logger.info("Grouping Volumes by Host Group")
        data = self.return_host_groups()

        self.groups = {}
        for each in data:

            try:
                self.groups[each['name']].append(each['vol'])
            except:
                self.groups[each['name']] = []
                self.groups[each['name']].append(each['vol'])
        return self.groups

    def ret_volumes(self):
        return self.set_volumes()

    def get_historical(self):
        self.set_volumes()
        self.vol_history = {}
        self.hostg_vol = {}
        for group in self.groups:

            self.hostg_vol[group] = {}
            for vol_name in self.groups[group]:
                try:
                    vol_hist = self.client.get_volume(vol_name, space=True, historical='1y')
                    logger.info("Getting Volume History for volume: " + vol_name)

                    tmphist = {}
                    for vol_entry in vol_hist:
                        if vol_entry['total'] == None:
                            vol_entry['total'] = 0
                        if vol_entry['snapshots'] == None:
                            vol_entry['snapshots'] = 0
                        if vol_entry['size'] == None:
                            vol_entry['size'] = 0
                        tmphist[vol_entry['time']] = vol_entry
                    self.vol_history[vol_name] = tmphist
                    self.hostg_vol[group][vol_name] = vol_hist
                    # self.hostg_vol[group][vol['name']] = tmphist


                except Exception as e:
                    pass

        return self.vol_history

    def calc_volumes(self):

        for group in self.groups:

            for volume in self.groups[group]:
                pass

    def calc_hgroups(self):
        logger.info("Calculating Host Group Data from Volume History")
        self.get_historical()

        self.all_gps = {}

        for group in self.groups:
            logger.info("Calculating for Group: " + group)

            # Find all the sample times
            # First get a set of all times that exist for volumes
            # in this host group
            times = set()
            for volume in self.groups[group]:
                try:
                    for htime in self.vol_history[volume]:
                        # print(htime)
                        times.add(htime)
                except:
                    pass

            self.all_gps[group] = {}

            for time in times:

                total = 0
                snapshots = 0
                size = 0

                try:
                    for volume in self.groups[group]:
                        total += self.vol_history[volume][time]['total']
                        snapshots += self.vol_history[volume][time]['snapshots']
                        size += self.vol_history[volume][time]['size']

                except:
                    pass
                try:
                    self.all_gps[group][time]['total'] = total
                    self.all_gps[group][time]['snapshots'] = snapshots
                    self.all_gps[group][time]['size'] = size
                    self.all_gps[group][time]['date'] = time
                except:
                    self.all_gps[group][time] = {}
                    self.all_gps[group][time]['total'] = total
                    self.all_gps[group][time]['snapshots'] = snapshots
                    self.all_gps[group][time]['size'] = size
                    self.all_gps[group][time]['date'] = time

            self.oput = {}
            for each in self.all_gps:
                self.oput[each] = {}
                for gp in self.all_gps[each]:
                    dto = datetime.strptime(gp, '%Y-%m-%dT%H:%M:%SZ')
                    out = dto.timestamp()
                    self.oput[each][out] = self.all_gps[each][gp]

            ret_out = {}
            for group in self.oput:
                ret_out[group] = []
                for tstamp in sorted(self.oput[group].keys()):
                    ret_out[group].append(self.oput[group][tstamp])

        self.calculated_hgroups = ret_out

    def build_series_data(self, group):

        volumes = self.groups[group]
        ret_data = {}

        for volume in volumes:
            try:
                ret_data[volume] = self.hostg_vol[group][volume]
            except:
                pass

        return ret_data


def write_array_data(workbook, worksheet, data):
    logger.info("Writing Array data")
    bold = workbook.add_format({'bold': True})
    worksheet.write('A1', 'Array Totals', bold)
    worksheet.write('A2', 'Date', bold)
    worksheet.write('B2', 'Total', bold)
    worksheet.write('C2', 'Snapshots', bold)
    worksheet.write('D2', 'Provisioned', bold)
    worksheet.write('E2', 'Capacity', bold)

    row = 2
    for each in data:
        total = round(each['total'] / 1024 / 1024 / 1024, 2)
        snapshots = round(each['snapshots'] / 1024 / 1024 / 1024, 2)
        provisioned = round(each['provisioned'] / 1024 / 1024 / 1024, 2)
        capacity = round(each['capacity'] / 1024 / 1024 / 1024, 2)

        worksheet.write(row, 0, each['time'])
        worksheet.write_number(row, 1, total)
        worksheet.write(row, 2, snapshots)
        worksheet.write(row, 3, provisioned)
        worksheet.write(row, 4, capacity)
        row += 1

    ret = {
        'dates': (2, 0, row, 0),
        'total': (2, 1, row, 1),
        'snapshots': (2, 2, row, 2),
        'provisioned': (2, 3, row, 3),
        'capacity': (2, 4, row, 4),
    }

    return ret


def write_hgroup_data(workbook, worksheet, data):
    bold = workbook.add_format({'bold': True})

    worksheet.write('A1', 'Host Group Totals')
    worksheet.write('A2', 'Date', bold)
    worksheet.write('B2', 'Snapshots', bold)
    worksheet.write('C2', 'Size', bold)
    worksheet.write('D2', 'Total', bold)

    row = 2
    for each in data:
        total = round(each['total'] / 1024 / 1024 / 1024, 2)
        snapshots = round(each['snapshots'] / 1024 / 1024 / 1024, 2)
        size = round(each['size'] / 1024 / 1024 / 1024, 2)

        worksheet.write(row, 0, each['date'])
        worksheet.write_number(row, 1, snapshots)
        worksheet.write(row, 2, total)
        worksheet.write(row, 3, size)
        row += 1

    ret = {
        'dates': (2, 0, row, 0),
        'total': (2, 1, row, 1),
        'snapshots': (2, 2, row, 2),
        'size': (2, 3, row, 3),
    }
    return ret

def write_exec_data(workbook, worksheet, data):
    logger.info("Writing Executive Data Sheet")

    bold = workbook.add_format({'bold': True})

    ret_vols = {}

    col = 1
    # row = 2
    for group in data:

        row = 2
        worksheet.write(0, col, group, bold)
        worksheet.write(1, col, 'Date', bold)
        worksheet.write(1, col + 1, 'Total', bold)
        worksheet.write(1, col + 2, 'Snapshots', bold)
        worksheet.write(1, col + 3, 'Size', bold)
        for each in data[group]:
            total = round(each['total'] / 1024 / 1024 / 1024)
            snapshots = round(each['snapshots'] / 1024 / 1024 / 1024)
            size = round(each['size'] / 1024 / 1024 / 1024)

            worksheet.write(row, col, each['date'])
            worksheet.write(row, (col + 1), total)
            worksheet.write(row, (col + 2), snapshots)
            worksheet.write(row, (col + 3), size)
            row += 1

        ret_vols[group] = {
            'dates': (2, col, row, col),
            'total': (2, col + 1, row, col + 1),
            'snapshots': (2, col + 2, row, col + 2),
            'size': (2, col + 3, row, col + 3)
        }
        col += 5
    return ret_vols

def write_hgroup_vol_data(workbook, worksheet, data):
    logger.info("Writing Host Group Volume data")

    bold = workbook.add_format({'bold': True})

    ret_vols = {}

    col = 5
    row = 2
    for volume in data:

        row = 2
        worksheet.write(0, col, volume, bold)
        worksheet.write(1, col, 'Date', bold)
        worksheet.write(1, col + 1, 'Total', bold)
        worksheet.write(1, col + 2, 'Snaps', bold)
        worksheet.write(1, col + 3, 'Size', bold)
        for each in data[volume]:
            total = round(each['total'] / 1024 / 1024 / 1024)
            snapshots = round(each['snapshots'] / 1024 / 1024 / 1024)
            size = round(each['size'] / 1024 / 1024 / 1024)

            worksheet.write(row, col, each['time'])
            worksheet.write(row, (col + 1), total)
            worksheet.write(row, (col + 2), snapshots)
            worksheet.write(row, (col + 3), size)
            row += 1

        ret_vols[volume] = {
            'dates': (2, col, row, col),
            'total': (2, col + 1, row, col + 1),
            'snapshots': (2, col + 2, row, col + 2),
            'size': (2, col + 3, row, col + 3)
        }
        col += 5

    return ret_vols


def calculate_exec_report(arrRepClasses):
    groupnames = set()
    exec_data_all = []
    for arrayReport in arrRepClasses:
        exec_rec = {}
        for group in arrayReport.calculated_hgroups:
            groupnames.add(group)

            exec_rec[group] = {}
            for record in arrayReport.calculated_hgroups[group]:
                dto = datetime.strptime(record['date'], '%Y-%m-%dT%H:%M:%SZ')
                dto = dto.strftime("%m/%d/%Y")
                exec_rec[group][dto] = record
        exec_data_all.append(exec_rec)
    #print(json.dumps(exec_data_all, indent=4))
    #sys.exit()
    '''
    [
        {
            "DR-ESXi-HG": {
                "02/06/2020": {
                    "total": 69676015530,
                    "snapshots": 0,
                    "size": 9895604649984,
                    "date": "2020-02-06T21:29:08Z"
                },
                "02/07/2020": {
                    "total": 69708036900,
                    "snapshots": 0,
                    "size": 9895604649984,
                    "date": "2020-02-07T21:29:08Z"
                }
    '''

    groupnames = list(groupnames)

    ret_data = {}
    for search_group in groupnames:

        ret_data[search_group] = {}
        for array_recs in exec_data_all:

            try:
                # Groups match
                for dt_ky in array_recs[search_group]:
                    try:
                        try:
                            ret_data[search_group][dt_ky]['total'] += array_recs[search_group][dt_ky]['total']
                            ret_data[search_group][dt_ky]['snapshots'] += array_recs[search_group][dt_ky]['snapshots']
                            ret_data[search_group][dt_ky]['size'] += array_recs[search_group][dt_ky]['size']
                        except:
                            array_recs[search_group][dt_ky]['date'] = dt_ky
                            ret_data[search_group][dt_ky] = array_recs[search_group][dt_ky]
                    except:
                        pass
            except:
                # Groups don't match
                pass
    # transform keys to timestamps
    #print(json.dumps(ret_data, indent=4))
    #sys.exit()
    ret_out = {}
    for group in ret_data:
        ret_out[group] = {}
        for dt in ret_data[group]:
            logger.info(dt)
            dto = datetime.strptime(dt, '%m/%d/%Y')
            ts = dto.timestamp()

            ret_out[group][ts] = ret_data[group][dt]
    #print(json.dumps(ret_out, indent=4))
    #sys.exit()
    final_output = {}
    for group in ret_out:

        final_output[group] = []
        kys = sorted(ret_out[group].keys())
        num_keys = len(kys)
        skip_num = num_keys / 11
        skip_num = int(skip_num)
        #logger.info("NUM_KEYS: " + str(num_keys))
        #logger.info("SKIP NUM: " + str(skip_num))

        ndx = 1
        okeys = []
        for ky in kys:
            if ndx == skip_num:
                okeys.append(ky)
                logger.info("KY: " + str(ky))
                ndx = 1
            ndx += 1

        for each in okeys:
            final_output[group].append(ret_out[group][each])

    return final_output
    #print(json.dumps(final_output, indent=4))



