#!/usr/bin/python3

"""
This module is used to add some JIRA queries on top of the Python JIRA module.
"""
import json
import requests

from requests_kerberos import HTTPKerberosAuth
from requests.auth import HTTPBasicAuth


class JiraClient:

    """ A jira component used to create connections to jira
        and do jira related tasks
    """

    def __init__(self, url, authtype, username=None, password=None):
        """Returns a JiraClient object
        :param string url : url to conenct to jira
        :param string authtype  : type of authentication needed to connect to
        jira
        :param string username : username for connecting to jira (basic auth)
        :param string password : password for connecting to jira (basic auth)
        """
        self.host = url
        self.url = url + "/rest/api/3/"
        self.authtype = authtype
        self.username = username
        self.password = password
        self._req_kwargs = None
        self.headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'}


    @property
    def req_kwargs(self):
        """ Set the key-word arguments for python-requests depending on the
        auth type. This code should run on demand exactly once, which is
        why it is a property.
        :return dict _req_kwargs: dict with the right options to pass in
        """
        if self._req_kwargs is None:
            if self.authtype == 'kerberos':
                # First we get a cookie from the "step" site, which is just
                # an nginx proxy that is kerberos enabled.
                step_url = self.host + '/step-auth-gss'
                conf_resp = requests.get(step_url, auth=self.get_auth_object())
                conf_resp.raise_for_status()
                # Going forward, we just pass in "cookies", no need to provide
                # an auth object anymore. In fact if we do, it'll get
                # preferred and fail since the service itself is not kerberos
                # enabled.
                self._req_kwargs = {'cookies': conf_resp.cookies}
            elif self.authtype == 'basic':
                self._req_kwargs = {'auth': self.get_auth_object()}
        return self._req_kwargs

    def get_auth_object(self):
        """ Returns Auth object based on auth type
        :return : Auth Object
        """
        if self.authtype == 'kerberos':
            return HTTPKerberosAuth(mutual_authentication=False)
        elif self.authtype == "basic":
            # useful for testing and debugging
            return HTTPBasicAuth(self.username, self.password)
        else:
            raise ValueError("Invalid auth type")

    def add_share_permissions(self, filter_id):
        """
        Updates the share permissions for a filter to share with any
        logged in user.

        :param String filter_id: The filter ID to update
        :return: Nothing
        """
        import pdb; pdb.set_trace()
        params = {
            'type': 'authenticated'
        }
        resp = requests.post(self.host + f"/rest/api/3/filter/{filter_id}/permission", data=json.dumps(params),
                             headers=self.headers, **self.req_kwargs)
        import pdb; pdb.set_trace()
        resp.raise_for_status()

    def create_board(self, name, project, filter_id, type='scrum'):
        """
        Updates a boards filter based on a filter ID.
        Note: Project is not used but kept for future updates to
        JIRA to specify board location.

        :param String name: Board ID
        :param String project: Project name
        :param String filter_id: Filter ID
        :param String type: Type of board to create
        :return: Response
        :rtype: JSON
        """
        params = {
            'name': name,
            'type': type,
            'filterId': filter_id
            }
        resp = requests.post(self.host + '/rest/agile/1.0/board', data=json.dumps(params),
                             headers=self.headers, **self.req_kwargs)
        resp.raise_for_status()
        return resp.json()

    def get_favourite_filters(self):
        """
        Get all favorite filters for user.
        """
        resp = requests.get(self.host + "/rest/api/2/filter/favourite",
                            headers=self.headers, **self.req_kwargs)
        resp.raise_for_status()
        return resp.json()

    def create_filter(self, name, jql, favorite=False):
        """
        Create a filter

        :param String name: Name of filter
        :param String jql: JQL to use for filter
        :param Bool favorite: Set this filter as favourite (default = False)
        :return: Response
        :rtype: JSON
        """
        params = {
            'name': name,
            'jql': jql,
            'favourite': favorite
        }
        resp = requests.post(self.host + f"/rest/api/2/filter",
                             headers=self.headers,
                             data=json.dumps(params),
                             **self.req_kwargs)
        resp.raise_for_status()
        return resp.json()

    def update_filter(self, name, jql, filter_id):
        """
        Function to update a filter.

        :param String name: Filter Name
        :param String jql: Filter JQL
        :param Int filter_id: Filter ID
        """
        params = {
            'name': name,
            'jql': jql,
        }
        resp = requests.put(self.host + f"/rest/api/2/filter/{filter_id}",
                            headers=self.headers,
                            data=json.dumps(params),
                            **self.req_kwargs)

        resp.raise_for_status()