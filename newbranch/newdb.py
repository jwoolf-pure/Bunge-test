from lib.db import *
from lib.utils import read_settings
import sys
from purestorage import FlashArray
from lib.utils import settings
import json



if __name__ == "__main__":

    settings = read_settings('settings.yml')
    arrays = settings.get('ARRAYS', None)
    if not arrays:
        print("Error getting array configuration from settings.yml file.")
        sys.exit(1)

    db_file = "sqlite_db.db"
    conn = create_connection(db_file)
    create_table(conn, sql_create_projects_table)

    cur = conn.cursor()

    array_volumes = {}
    for array in arrays:
        array_volumes[array['name']] = []
        fa = FlashArray(array['address'], api_token=array['token'])

        volumes = fa.list_volumes()
        for volume in volumes:
            array_volumes[array['name']].append(volume['name'])
    #print(json.dumps(array_volumes, indent=4))
    #sys.exit()


    for array in arrays:
        fa = FlashArray(array['address'], api_token=array['token'])
        for volume in array_volumes[array['name']]:
            samples = fa.get_volume(volume, space=True, historical='1y')
            for sample in samples:
                volume_insert(conn, array['name'], sample['name'], sample['total'],
                              sample['size'], sample['snapshots'], sample['time'])
                print(json.dumps(sample, indent=4))
            conn.commit()


