# AWS MFA Credentials Updater

> A convinient tool to update credentials for an AWS profile with MFA using a virtual device.

## Installation

Install it from PyPi

```sh
pip install aws-credentialer
```

## Usage

### Pre-requisite

You must have configured the AWS CLI. The `config` and `credentials` file must have two profiles: `default` and `mfa`. And add the following line to the `default` profile:

```ini
mfa_arn = <virtual_mfa_serial_number>
```

### CAUTION

This tool will override the `~/.aws/credentials/` file.

### Usage Example

Run the following command in your favorite terminal, where `nnnnnn` is the token from the virtual device configured with AWS.

```sh
python -m aws_credentialer nnnnnn
```

Help is available with the `-h` parameter.

## Release History

* 0.1.0
  * The first proper release.
