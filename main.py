import argparse
import boto3
import botocore.exceptions
import configparser
import datetime
import logging
import sys

from os import path
from argparse import RawTextHelpFormatter
from datetime import datetime

HEADER = 'AWS Credentials Helper for MFA Profile'
EXAMPLE = '''Example(s):

> aws-credentialer nnnnnn
> aws-credentialer -d nnnnnn
'''

parser = argparse.ArgumentParser(formatter_class=RawTextHelpFormatter,
                                 description=HEADER, epilog=EXAMPLE)
parser.add_argument('-d', '--debug', help='display debug logs', action='store_true')
parser.add_argument('token', help='aws six (6) digit MFA token', type=str)
args = parser.parse_args()

debug = True if args.debug else False

if debug:
    print('i was here')
    logging.basicConfig(level=logging.DEBUG)

session = boto3.Session()

try:
    mfa_arn = session._session.full_config['profiles']['default']['mfa_arn']
    logging.info(f'AWS MFA ARN: {mfa_arn}')
except:
    message = 'AWS MFA ARN in the default profile not found'
    logging.error(message)
    sys.exit(f'{message}\nTerminating')

token = args.token
if token is None:
    token = input('\nPlease enter your six (6) digit MFA token: ')

if token is None or token == "" or len(token) != 6:
    message = 'Invalid MFA token entered'
    logging.error(message)
    sys.exit(f'{message}\nTerminating')

logging.debug(f'Now:             {datetime.utcnow()}')
sts = session.client('sts')
try:
    validated_token = sts.get_session_token(DurationSeconds=86400, SerialNumber=mfa_arn, TokenCode=token)
except botocore.exceptions.ClientError as e:
    message='Invalid or expired MFA token entered'
    logging.error(message)
    sys.exit(f'{message}\nTerminating')

rem_cred = validated_token['Credentials']
logging.debug(f'AccessKeyId:     {rem_cred.get("AccessKeyId")}')
logging.debug(f'SecretAccessKey: {rem_cred.get("SecretAccessKey")}')
logging.debug(f'SessionToken:    {rem_cred.get("SessionToken")}')
logging.debug(f'Expiration:      {rem_cred.get("Expiration")}')

filepath = '~/.aws/credentials'
if '~' in filepath:
    filepath = path.expanduser(filepath)
fullpath = path.realpath(filepath)

choice = input(f'Are you sure you want to modify {fullpath}? [yN]')
if choice.upper() != 'Y':
    message = f'Not modifying {fullpath}'
    logging.error(message)
    sys.exit(f'{message}\nTerminating')

loc_cred = configparser.ConfigParser()
with open(fullpath, 'r') as cf:
    loc_cred.read_file(cf)

loc_cred.set('mfa','aws_access_key_id', rem_cred.get('AccessKeyId'))
loc_cred.set('mfa','aws_secret_access_key', rem_cred.get('SecretAccessKey'))
loc_cred.set('mfa','aws_session_token', rem_cred.get('SessionToken'))
with open(fullpath, 'w') as cf:
    loc_cred.write(cf)
print(f'{fullpath} updated')