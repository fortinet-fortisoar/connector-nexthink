""" Copyright start
  Copyright (C) 2008 - 2023 Fortinet Inc.
  All rights reserved.
  FORTINET CONFIDENTIAL & FORTINET PROPRIETARY SOURCE CODE
  Copyright end """

from requests import request, exceptions as req_exceptions
from connectors.core.connector import get_logger, ConnectorError


logger = get_logger("nexthink")


class Nexthink:
    def __init__(self, config, *args, **kwargs):
        server_url = config.get("server_url")
        if not server_url.startswith('https://') and not server_url.startswith('http://'):
            server_url = "https://"+server_url
        self.url = server_url
        self.username = str(config.get("username"))
        self.password = str(config.get("password"))
        self.verify_ssl = config.get("verify_ssl")

    def api_request(self, method, endpoint, params={}):
        try:
            endpoint = self.url + endpoint
            logger.debug(f"\n-------------req start-------------\n{method} {endpoint}\nauth: {self.username} - {self.password}\nparams: {params}\nverify: {self.verify_ssl}\n")
            response = request(method, endpoint, auth=(self.username, self.password), params=params, verify=self.verify_ssl)

            if response.status_code in [200, 201, 204]:
                if response.text != "":
                    return response.json()
                else:
                    return True
            else:
                if response.text != "":
                    err_resp = response.json()
                    error_msg = 'Response [{0}:{1} Details: {2}]'.format(response.status_code, response.reason, err_resp)
                else:
                    error_msg = 'Response [{0}:{1}]'.format(response.status_code, response.reason)
                logger.error(error_msg)
                raise ConnectorError(error_msg)
        except req_exceptions.SSLError:
            logger.error('An SSL error occurred')
            raise ConnectorError('An SSL error occurred')
        except req_exceptions.ConnectionError:
            logger.error('A connection error occurred')
            raise ConnectorError('A connection error occurred')
        except req_exceptions.Timeout:
            logger.error('The request timed out')
            raise ConnectorError('The request timed out')
        except req_exceptions.RequestException:
            logger.error('There was an error while handling the request')
            raise ConnectorError('There was an error while handling the request')
        except Exception as err:
            raise ConnectorError(str(err))


def nexthink_query_language(config, params):
    ob = Nexthink(config)
    params.update({"format": "json"})
    return ob.api_request("GET", "/2/query", params=params)


def check_health_ex(config):
    try:
        params = {
            "query": "(select (name) (from device) (limit 1))",
            "platform": "windows",
        }
        nexthink_query_language(config, params)
        return True
    except Exception as err:
        raise ConnectorError(str(err))


operations = {
    "nexthink_query_language": nexthink_query_language
}
