Config File
===========
The config file is made up of multiple parts

.. code-block:: python

        'operational_q1_start': '01-01-19',

* This date (month-day-year) is used to standardize Q1 start times across teams and will be globally set.

    .. note:: 2 weeks sprints must be within 1 week of this date, and 3 weeks sprints within 10 days.

.. code-block:: python

        'run_for_quarter': 'Y20-Q4',
        'run_for_quarter': False,

* This optional value can be set to a quarter label to run the utility for a specific quarter upto 10 years in the future.

    .. note:: Set this to :code:`False` if you want to disable this.

.. code-block:: python

        'default_jira_instance': 'example',

* This value specifies the default JIRA instance to use in case one is not provided in the team

.. code-block:: python

        # JIRA instances
        'jira': {
            'example': {
                'options': {
                    'server': 'JIRA URL',
                    'verify': True,
                },
                'basic_auth': ('USERNAME', 'PASSWORD'),
            },
        },

* This dictionary is used to set up multiple JIRA instances for multiple teams

.. code-block:: python

        # Teams and relevant information
        'teams': {
            'TEAM_NAME': {
                'jira_project': 'FACTORY',
                'sprint_length': 2,
                'jira_instance': 'example',
                'sprint_start_date': '01-08-19'
            }
        }

* This dictionary is used to set up the teams.

    * The :code:`jira_project` is used to determine what JIRA project to use
    * The :code:`sprint_length` is used to determine what sprint length to use (2 or 3 weeks)
    * The :code:`jira_instance` is used to specify what JIRA instance to use. If left blank the default one will be used.
    * The :code:`sprint_start_date` is used to determine what date the team will start their sprints.

        .. note:: 2 week sprints have to be within 1 week of :code:`operational_q1_start` and 3 week sprints within 10 days.
