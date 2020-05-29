#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import argparse

from spaceone.identity.manager.token_manager import JWTManager

def _init_parser():
    parser = argparse.ArgumentParser(description='Token Issuer', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('user_id', metavar='<user_id>', help='User Id')
    parser.add_argument('domain_id', metavar='<domain_id>', help='Domain Id')
    parser.add_argument('-f', type=argparse.FileType('r'), help='Private JWK File Path', dest='jwk_file', required=True)
    parser.add_argument('--user-type', help='User Type', default='USER', dest='user_type', choices=['USER', 'DOMAIN_OWNER'])
    parser.add_argument('--ttl', help='Maximum Refresh Count', type=int, default=6)
    parser.add_argument('--token-timeout', help='Access Token Timeout', type=int, default=1800)
    parser.add_argument('--refresh-timeout', help='Refresh Token Timeout', type=int, default=3600)
    return parser


def _load_jwk(jwk_json):
    try:
        return json.loads(jwk_json)
    except Exception as e:
        raise Exception(f'JWK Format is invalid. ({e})')


def _print_key(access_token, refresh_token):
    print('Access Token:')
    print(access_token)
    print()
    print('Refresh Token:')
    print(refresh_token)


if __name__ == '__main__':
    parser = _init_parser()
    args = parser.parse_args()
    private_jwk = _load_jwk(args.jwk_file.read())

    jwt_mgr = JWTManager()
    access_token = jwt_mgr.issue_access_token(args.user_type, args.user_id, args.domain_id,
                                              private_jwk=private_jwk, timeout=args.token_timeout)
    refresh_token = jwt_mgr.issue_refresh_token(args.user_type, args.user_id, args.domain_id,
                                                private_jwk=private_jwk, timeout=args.refresh_timeout, ttl=args.ttl)

    _print_key(access_token, refresh_token)
