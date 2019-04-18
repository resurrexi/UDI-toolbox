from gudid_selenium import GUDID
from datetime import datetime
import logging
import argparse
import pandas as pd

logging.basicConfig(format='[%(levelname)s] %(message)s',
                    level=logging.INFO)

parser = argparse.ArgumentParser()
parser.add_argument('-u', '--user', required=True,
                    help='GUDID user')
parser.add_argument('-w', '--password', required=True,
                    help='GUDID password')
parser.add_argument('-f', '--file', required=True,
                    help='path to CSV with records to add')
parser.add_argument('-d', '--date', required=True,
                    help='publish date for all records')
args = vars(parser.parse_args())

# load csv
df = pd.read_csv(args['file'])
records = df.to_dict(orient='records')
first_record = records[0]  # comment out later

# set pub date to arg or today
now = datetime.now().strftime('%Y-%m-%d')
if args['date'] < now:
    logging.info("Date argument < today. Setting pub date to today.")
    pub_date = now
else:
    pub_date = args['date']

# load browser
mybrowser = GUDID(args['user'], args['password'])
mybrowser.load_base_url()
mybrowser.login()
mybrowser.load_manage_page()

# iterate and add records
for record in records:
    logging.info("Adding {}".format(record['Unit UDI']))
    mybrowser.load_new_device_page()
    result = mybrowser.fill_new_device_form(record, args['date'])
    # check if result is True or False
    # if False, then the record already existed so skip it
    if result is False:
        continue  # goto next record
    mybrowser.save_new_device_draft()
