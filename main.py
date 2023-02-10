import boto3
import configparser
import datetime
import logging
import os

# logging.basicConfig(level=logging.DEBUG)
session = boto3.Session()

try:
    mfa_arn = session._session.full_config['profiles']['default']['mfa_arn']
except:
    message = 'AWS MFA ARN in the default profile not found'
    logging.error(message)
    sys.exit(f'{message}\nTerminating')

logging.info(f'AWS MFA ARN: {mfa_arn}')
token = input('\nPlease enter your six (6) digit MFA token: ')
if token == "" or len(token) != 6:
    message = 'Invalid MFA token entered'
    logging.error(message)
    sys.exit(f'{message}\nTerminating')

sts = session.client('sts')
validated_token = sts.get_session_token(DurationSeconds=86400, SerialNumber=mfa_arn, TokenCode=token)
rem_cred = validated_token['Credentials']

logging.debug(f'AccessKeyId:     {rem_cred.get("AccessKeyId")}')
logging.debug(f'SecretAccessKey: {rem_cred.get("SecretAccessKey")}')
logging.debug(f'SessionToken:    {rem_cred.get("SessionToken")}')
logging.debug(f'Expiration:      {rem_cred.get("Expiration")}')
logging.debug(f'Now:             {datetime.datetime.utcnow()}')

filepath = 'credentials'
filepath = '/Users/hidayatullah/.df/aws/credentials'
filepath = '~/.aws/credentials'
if '~' in filepath:
    filepath = os.path.expanduser(filepath)
fullpath = os.path.realpath(filepath)

loc_cred = configparser.ConfigParser()
with open(fullpath, 'r') as cf:
    loc_cred.read_file(cf)

loc_cred.set('mfa','aws_access_key_id', rem_cred.get('AccessKeyId'))
loc_cred.set('mfa','aws_secret_access_key', rem_cred.get('SecretAccessKey'))
loc_cred.set('mfa','aws_session_token', rem_cred.get('SessionToken'))
with open(fullpath, 'w') as cf:
    loc_cred.write(cf)