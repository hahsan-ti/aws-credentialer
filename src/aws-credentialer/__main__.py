#!/usr/bin/env python3
"""
An AWS MFA Credentials Helper
"""
#pylint: disable=protected-access

from os import path
from argparse import RawTextHelpFormatter
from datetime import datetime

import argparse
import configparser
import logging
import sys
import boto3
import botocore.exceptions

HEADER = 'AWS Credentials Helper for MFA Profile'
EXAMPLE = '''Example(s):

> aws-credentialer nnnnnn
> aws-credentialer -d nnnnnn
'''

parser = argparse.ArgumentParser(description=HEADER, epilog=EXAMPLE)
parser.add_argument('-d', '--debug', help='display debug logs', action='store_true')
parser.add_argument('token', help='aws six (6) digit MFA token', type=str)
parser._print_message(parser.description)
args = parser.parse_args()

if args.debug:
    print('i was here')
    logging.basicConfig(level=logging.DEBUG)

session = boto3.Session()

try:
    mfa_arn = session._session.full_config['profiles']['default']['mfa_arn']
    logging.info('AWS MFA ARN: %s', mfa_arn)
except KeyError as e:
    sys.exit('AWS MFA ARN in the default profile not found')

token = args.token
if token is None:
    token = input('\nPlease enter your six (6) digit MFA token: ')

if token is None or token == "" or len(token) != 6:
    sys.exit('Invalid MFA token entered')

logging.debug('Now: %s',datetime.utcnow())
sts = session.client('sts')
try:
    validated_token = sts.get_session_token(DurationSeconds=86400,
                                            SerialNumber=mfa_arn,
                                            TokenCode=token)
except botocore.exceptions.ClientError as e:
    sys.exit('Invalid or expired MFA token entered')

rem_cred = validated_token['Credentials']
logging.debug('AccessKeyId: %s', rem_cred.get("AccessKeyId"))
logging.debug('SecretAccessKey: %s', rem_cred.get("SecretAccessKey"))
logging.debug('SessionToken: %s', rem_cred.get("SessionToken"))
logging.debug('Expiration: %s', rem_cred.get("Expiration"))

FILEPATH = path.realpath(path.expanduser('~/.aws/credentials'))

choice = input(f'Are you sure you want to modify {FILEPATH}? [yN]')
if choice.upper() != 'Y':
    sys.exit(f'Not modifying {FILEPATH}')

loc_cred = configparser.ConfigParser()
with open(FILEPATH, 'r', encoding='utf8') as cf:
    loc_cred.read_file(cf)

loc_cred.set('mfa','aws_access_key_id', rem_cred.get('AccessKeyId'))
loc_cred.set('mfa','aws_secret_access_key', rem_cred.get('SecretAccessKey'))
loc_cred.set('mfa','aws_session_token', rem_cred.get('SessionToken'))
with open(FILEPATH, 'w', encoding='utf8') as cf:
    loc_cred.write(cf)
print(f'{FILEPATH} updated')
