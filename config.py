
config = {
    'SPS': {
        # Define the first day of Q1 (As a 0-padded number)
        'operational_q1_start': '01-01-19',

        # Optional: Run for quarter
        # Format: Y[operational year]-Q[operational quarter]
        # 'run_for_quarter': 'Y20-Q4',
        'run_for_quarter': False,

        # Default JIRA instance to use if none is provided
        'default_jira_instance': 'example',

        # JIRA instances
        'jira': {
            'example': {
                'options': {
                    'server': 'JIRA_URL',
                    'verify': True,
                },
                'basic_auth': ('USERNAME', 'PASSWORD'),
            },
        },

        # Teams and relevant information
        'teams': {
            'TEAM_NAME': {
                'jira_project': 'FACTORY',
                'sprint_length': 2,
                'jira_instance': 'example',
                'sprint_start_date': '01-7-19'
            }
        }

    }
}