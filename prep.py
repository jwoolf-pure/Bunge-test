from promrep.promclient import PromClient
from datetime import datetime, timedelta
import json

now = datetime.now()
delta = timedelta(weeks=1)
newtime = now - delta

ts = newtime.timestamp()
ot = datetime.now().timestamp()


print("TS: " + str(ts))
print("OT: " + str(ot))

st = ( ot - ts ) / 12

if __name__ == '__main__':

    handle = PromClient('http://10.21.167.124:9090')

    # res = handle.query('purefa_volume_performance_latency_usec{volume="DR-ESXi-VG/DR-VMFS-2"}', time=ts)
    res = handle.query_range('purefa_volume_performance_latency_usec{volume="DR-ESXi-VG/DR-VMFS-2", dimension="write"}', start=ts, end=ot, step = st)

    res = json.loads(res.content)
    #print(len(res['data']['result']))

    print(json.dumps(res, indent=4))


    #for each in res['data']['result']:
    #    dt = datetime.fromtimestamp(each['value'][0])
    #    print(dt)

    #ts = datetime.now().timestamp()
    #res = handle.query('purefa_volume_space_size_bytes{pod="DR_ri-sql-rdms-P-DATA02"}', time=ts)
    #res = json.loads(res.content)

    #for each in res['data']['result']:
    #    print(each['value'])
    #print(json.dumps(res, indent=4))