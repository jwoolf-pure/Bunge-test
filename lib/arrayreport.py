from purestorage import FlashArray
import urllib3
import logging
from datetime import datetime
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
urllib3_log = logging.getLogger("urllib3")
urllib3_log.setLevel(logging.CRITICAL)
logger = logging.getLogger('array_annual')
import json

suffixes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
def humansize(nbytes):
    i = 0
    while nbytes >= 1024 and i < len(suffixes) - 1:
        nbytes /= 1024.
        i += 1
    f = ('%.2f' % nbytes).rstrip('0').rstrip('.')
    return '%s %s' % (f, suffixes[i])


class ArrayReport:

    def __init__(self, address, token):
        self.client = FlashArray(address, api_token=token)

    def return_array_space(self, time):
        return self.client.get(space=True, historical=time)

    def return_host_groups(self):
        return self.client.list_hgroups(connect=True)

    def set_volumes(self):
        #logger.info("setting volumes")
        data = self.return_host_groups()

        self.groups = {}
        for each in data:

            try:
                self.groups[each['name']].append(each['vol'])
                #logger.info(each )
            except:
                self.groups[each['name']] = []
                self.groups[each['name']].append(each['vol'])
        # print("GROUPS")
        # print(json.dumps(self.groups, indent=4))
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

        # print("VOLHIST")
        # print(json.dumps(self.vol_history, indent=4))
        return self.vol_history

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

        # print("ALLGPS")
        # print(json.dumps(self.all_gps, indent=4))
        # print("FINAL")
        # print(json.dumps(ret_out, indent=4))
        self.calculated_hgroups = ret_out


def write_array_data(workbook, worksheet, data):

    logger.info("Writing Array data")
    bold = workbook.add_format({'bold': True})

    worksheet.write('A1', 'Date', bold)
    worksheet.write('B1', 'Total', bold)
    worksheet.write('C1', 'Snapshots', bold)
    worksheet.write('D1', 'Provisioned', bold)
    worksheet.write('E1', 'Capacity', bold)

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
    logger.info("Writing Host Group data")
    bold = workbook.add_format({'bold': True})

    worksheet.write('A1', 'Date', bold)
    worksheet.write('B1', 'Snapshots', bold)
    worksheet.write('C1', 'Size', bold)
    worksheet.write('D1', 'Total', bold)

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
