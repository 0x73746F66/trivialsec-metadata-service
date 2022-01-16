import ipaddress
import re
import errno
import json
import ssl
from binascii import hexlify
from pathlib import Path
from os import path
from socket import socket, error as SocketError, getaddrinfo, AF_INET6, AF_INET, SOCK_STREAM
from base64 import urlsafe_b64encode
from urllib.parse import urlparse, parse_qs
from cryptography import x509
from cryptography.x509 import extensions
from OpenSSL.crypto import load_certificate, dump_certificate, X509, X509Name, TYPE_RSA, TYPE_DSA, TYPE_DH, TYPE_EC, FILETYPE_ASN1, FILETYPE_PEM
from OpenSSL import SSL
from ssl import create_default_context, SSLCertVerificationError, Purpose, CertificateError
from datetime import datetime
import requests
from certvalidator import CertificateValidator, ValidationContext
from certvalidator.errors import PathValidationError, RevokedError, InvalidCertificateError, PathBuildingError
from bs4 import BeautifulSoup as bs
from dns import query, zone, resolver, rdtypes
from dns.exception import DNSException
from aslookup import get_as_data
from aslookup.exceptions import NoASDataError, NonroutableAddressError, AddressFormatError
from retry.api import retry
from requests.status_codes import _codes
from requests.adapters import HTTPAdapter
from requests.exceptions import ReadTimeout, ConnectTimeout
from urllib3.exceptions import ConnectTimeoutError, SSLError, MaxRetryError, NewConnectionError
from urllib3.connectionpool import HTTPSConnectionPool
from urllib3.poolmanager import PoolManager, SSL_KEYWORDS

HTTP_503 = 'Service Unavailable'
HTTP_504 = 'Gateway Timeout'
HTTP_598 = 'Network read timeout error'
HTTP_599 = 'Network connect timeout error'
TLS_ERROR = 'TLS handshake failure'
SSL_DATE_FMT = r'%b %d %H:%M:%S %Y %Z'
X509_DATE_FMT = r'%Y%m%d%H%M%SZ'
SEMVER_REGEX = r'\d+(=?\.(\d+(=?\.(\d+)*)*)*)*'
DOCSTRING_REGEX = r"\/\*([\s\S]*?)\*\/"

class SafeBrowsingInvalidApiKey(Exception):
    def __init__(self):
        Exception.__init__(self, "Invalid API key for Google Safe Browsing")

class SafeBrowsingWeirdError(Exception):
    def __init__(self, code, status, message, details):
        self.message = "%s(%i): %s (%s)" % (
            status,
            code,
            message,
            details
        )
        Exception.__init__(self, message)

class SafeBrowsing:
    def __init__(self, key):
        self.api_key = key

    def lookup_urls(self, urls :list, platforms :list = None):
        if platforms is None:
            platforms = ["ANY_PLATFORM"]

        proxies = None
        if config.http_proxy or config.https_proxy:
            proxies = {
                'http': f'http://{config.http_proxy}',
                'https': f'https://{config.https_proxy}'
            }
        data = {
            "client": {
                "clientId": "trivialsec-common",
                "clientVersion": config.app_version
            },
            "threatInfo": {
                "threatTypes":
                    [
                        "MALWARE",
                        "SOCIAL_ENGINEERING",
                        "THREAT_TYPE_UNSPECIFIED",
                        "UNWANTED_SOFTWARE",
                        "POTENTIALLY_HARMFUL_APPLICATION"
                    ],
                "platformTypes": platforms,
                "threatEntryTypes": ["URL"],
                "threatEntries": [{'url': u} for u in urls]
            }
        }
        headers = {'Content-type': 'application/json'}

        res = requests.post(
                'https://safebrowsing.googleapis.com/v4/threatMatches:find',
                data=json.dumps(data),
                params={'key': self.api_key},
                headers=headers,
                proxies=proxies,
                timeout=3
        )
        if res.status_code == 200:
            # Return clean results
            if res.json() == {}:
                return {u: {'malicious': False} for u in urls}
            result = {}
            for url in urls:
                # Get matches
                matches = [match for match in res.json()['matches'] if match['threat']['url'] == url]
                if len(matches) > 0:
                    result[url] = {
                        'malicious': True,
                        'platforms': { platform['platformType'] for platform in matches },
                        'threats': { threat['threatType'] for threat in matches },
                        'cache': min([b["cacheDuration"] for b in matches])
                    }
                else:
                    result[url] = {"malicious": False}
            return result
        if res.status_code == 400:
            if 'API key not valid' in res.json()['error']['message']:
                raise SafeBrowsingInvalidApiKey()
            raise SafeBrowsingWeirdError(
                res.json()['error']['code'],
                res.json()['error']['status'],
                res.json()['error']['message'],
                res.json()['error']['details']
            )
        raise SafeBrowsingWeirdError(res.status_code, "", "", "")

    def lookup_url(self, url :str, platforms :list = None):
        if platforms is None:
            platforms = ["ANY_PLATFORM"]
        return self.lookup_urls([url], platforms=platforms)[url]
