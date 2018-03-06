#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2018 theloop Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import json
import sys
import argparse
import os

from icxcli.cmd import wallet
from icxcli.icx import NonExistKey
from icxcli.cmd.wallet import ExitCode
from icxcli import __version__


def main():
    """
    Main procedure
    :return:
    """
    command, parser = parse_args()
    sys.exit(call_wallet_method(command, parser))


def check_required_argument_in_args(**kwargs):
    """Make sure user has entered all the required arguments.

    :return:
    True when arguments are valid.
    False when arguments are invalid.
    """
    flag = True
    for key, value in kwargs.items():
        flag = flag and bool(value)
    return flag


def parse_args():
    """ Get arguments from CLI and parse the arguments.

    :return: command, parser
    """

    parser = argparse.ArgumentParser(prog='icli.py', usage='''
        Normal commands:
            version
            help

        Wallet Commands:
            wallet create <file path> -p <password>  | --networkid <testnet>
            wallet show <file path> -p <password>   | --networkid <testnet>
            asset list <file path> -p <password>        | --networkid <testnet>
            transfer  <to> <amount> <file path> -p <password> -f <fee> -d <decimal point=18>  | --n <network id>

        IF YOU MISS --networkid, icli WILL USE MAINNET.

          ''')

    parser.add_argument('command', nargs='*', help='wallet create, wallet show, asset list, transfer')
    parser.add_argument('-p', dest='password'
                        , help='password')
    parser.add_argument('-f', dest='fee'
                        , help='transaction fee')
    parser.add_argument('-d', dest='decimal_point'
                        , help='decimal point', default=18)
    parser.add_argument('-n', dest='network_id'
                        , help='which network', default='mainnet')

    args = parser.parse_args()

    command = ' '.join(args.command[:2])

    return command, parser


def call_wallet_method(command, parser):
    """ Call the specific wallet method when having right number of arguments.

    :param command: Command part of interface. type: str
    :param parser: ArgumentParser
    """

    args = parser.parse_args()
    try:
        url = get_selected_url(args.network_id)
    except NonExistKey:
        return ExitCode.DICTIONARY_HAS_NOT_KEY.value

    if len(args.command) > 1 and args.password is None:
        input_password = input("You missed your password! input your password : ")

    if command == 'wallet create' and len(args.command) == 3:
        return wallet.create_wallet(args.password, args.command[2])
    elif command == 'wallet show' and len(args.command) == 3:
        return wallet.show_wallet(args.password, args.command[2])
    elif command == 'asset list' and len(args.command) == 3:
        return wallet.show_asset_list(args.password, args.command[2])
    elif command.split(' ')[0] == 'transfer' and len(args.command) == 4 \
            and check_required_argument_in_args(fee=args.fee, decimal_point=args.decimal_point):
        return wallet.transfer_value_with_the_fee(
            args.password, args.fee, args.decimal_point, to=args.command[1],
            amount=args.command[2], file_path=args.command[3])
    elif command.split(' ')[0] == 'version':
        print(f"version : {__version__}")
    else:
        parser.print_help()
        return 0


def get_selected_url(network_id):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    with open(f"{current_dir}/network_conf.json", 'r') as f:
        network_config_json_str = f.read()
    network_config_json = json.loads(network_config_json_str)

    try:
        return network_config_json["networkid"][network_id]
    except KeyError:
        print(f"{network_id} is not valid network id")
        raise NonExistKey
