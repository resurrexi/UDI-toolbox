from gudid_selenium import GUDID
import pandas as pd
import logging
import argparse

logging.basicConfig(format='[%(levelname)s] %(message)s',
                    level=logging.INFO)

parser = argparse.ArgumentParser()
parser.add_argument('-u', '--user', required=True,
                    help='GUDID user')
parser.add_argument('-w', '--password', required=True,
                    help='GUDID password')
parser.add_argument('-f', '--file', required=True,
                    help='Path of file with GUDIDs to edit')
args = vars(parser.parse_args())

# load GUDIDs
df = pd.read_csv(args['file'])
gudids = df['Unit UDI'].tolist()

# load browser
mybrowser = GUDID(args['user'], args['password'])
mybrowser.load_base_url()
mybrowser.login()
mybrowser.load_manage_page()

for gudid in gudids:
    logging.info('Editing {}...'.format(gudid))
    mybrowser.find_record(gudid)
    mybrowser.edit_record()
