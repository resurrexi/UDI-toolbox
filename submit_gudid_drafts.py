from gudid_selenium import GUDID
from datetime import datetime
import logging
import argparse

logging.basicConfig(format='[%(levelname)s] %(message)s',
                    level=logging.INFO)

parser = argparse.ArgumentParser()
parser.add_argument('-u', '--user', required=True,
                    help='GUDID user')
parser.add_argument('-w', '--password', required=True,
                    help='GUDID password')
parser.add_argument('-d', '--date', required=True,
                    help='publish date for all records')
args = vars(parser.parse_args())

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
mybrowser.submit_all_device_drafts(pub_date)
