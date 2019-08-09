"""
This module is used to interact with the JIRA client.
"""
# Build In Modules
import logging
from SPU.jira_client import JiraClient

# 3rd Party Modules
import jira.client

# Local Modules
import SPU.main as m

# Global Variables
log = logging.getLogger(__name__)


def get_jira_client(team, config):
    """
    Function to match and create JIRA client.

    :param Dict team: team dict
    :param dict config: Config dict
    :returns: Matching JIRA client
    :rtype: jira.client.JIRA
    """
    # Use the Jira instance set in the team config. If none then
    # use the configured default jira instance.
    jira_instance = team.get('jira_instance', False)
    if not jira_instance:
        jira_instance = config['SPU'].get('default_jira_instance', False)
    if not jira_instance:
        log.error("   No jira_instance for issue and there is no default in the config")
        raise Exception

    client = jira.client.JIRA(**config['SPU']['jira'][jira_instance])
    return client


def get_boards(config, jiras):
    """
    Get all boards from all JIRA instances in the config file

    :param Dict config: Config Dict
    :param List jira: List of all JIRA clients in use
    :return: All boards
    :rtype: List
    """
    all_boards = {}
    for jira in jiras:
        client = get_jira_client(jira, config)
        boards = client.boards()
        for board in boards:
            all_boards[board.name] = board.id
    return all_boards


def create_sprints(new_board, calender, client):
    """
    Helper function to create sprints for a board.

    :param jira.resources.Board new_board: New JIRA Board
    :param Dict calender: Calender Dict
    :param jira.client.JIRA client: JIRA client
    :return: Nothing
    """
    sprints = []
    for sprint in calender:
        # Create our sprints
        sprint = client.create_sprint(
            name=sprint['sprint_string'],
            board_id=new_board['id'],
            # startDate=value['start_date'].strftime('%Y-%m-%dT%H:%M:00.000+10:0'),
            # endDate=value['end_date'].strftime('%Y-%m-%dT%H:%M:00.000+10:0'),
        )
        sprints.append(sprint)
    return sprints


def create_labels(team, name, calender, client, sprints):
    """
    Helper function to create labels for a project.

    :param Dict team: Team dict
    :param Dict calender: Calender dict
    :param jira.client.JIRA client: JIRA client
    :param String name: Team name
    :param List sprints: List of sprints
    :return: Newly Created Issue
    :rtype: jira.Issue
    """
    # There is no way to 'manage' labels.
    # See https://community.atlassian.com/t5/Jira-questions/How-to-manage-labels/qaq-p/296536
    # Best way is to create an issue for our new board

    # First gather our labels
    labels = []
    for sprint, value in calender.items():
        if value['quarter_string'] not in labels:
            labels.append(value['quarter_string'])

    # Create a new JIRA issue
    title = '%s Sprint Planning for %s-%s' % (
        name, calender[0]['quarter_string'], calender[0]['quarter_string']
    )
    issue = client.create_issue(fields={
        'summary': title,
        'issuetype': {'name': 'Story'},
        'labels': labels
    })

    # Add issue to first sprint
    client.add_issues_to_sprint(sprints[0].id, issue_keys=[issue.key])

    return issue


def create_filter(quarters_label, project, rest_api_client, glob=False):
    """
    Helper function to create filters for our sprint planning.

    :param String quarters_label: Quarter label we are using
    :param String project: Project we are working on
    :param SPS.jira_client rest_api_client: rest API JIRA client
    :param Bool glob: Is this a global filter (omit project)
    :return: Dict of newly created filters
    :rtype: Dict
    """
    if not glob:
        filter = rest_api_client.create_filter(
            name=f'{quarters_label} - {project} filter',
            jql=f"labels = '{quarters_label}' AND project = {project} ORDER BY Rank ASC",
            favorite=True
        )
        return filter
    else:
        filter = rest_api_client.create_filter(
            name=f'{project} filter',
            jql=f"labels = '{quarters_label}' ORDER BY Rank ASC",
            favorite=True
        )
        return filter


def get_global_filters(jira, config, bad_board=False):
    """
    Helper function to get all favorite filters.

    :param Dict jira: JIRA instance to use
    :param Dict config: Config file
    :param Bool bad_board: Should get get filters for the Bad Board
    :return: Global filters
    :rtype: List
    """
    if bad_board:
        title = m.GLOBAL_BAD_BOARD
    else:
        title = m.GLOBAL_BOARD

    # Get the rest API client
    jira_instance = config['SPU']['jira'].get(jira['jira_instance'], False)

    rest_api_client = JiraClient(
        url=jira_instance['options']['server'],
        authtype='basic',
        username=jira_instance['basic_auth'][0],
        password=jira_instance['basic_auth'][1]
    )
    resp = rest_api_client.get_favourite_filters()
    new_filters = []
    for fil in resp:
        if title in fil['name']:
            new_filters.append(fil)
    return new_filters


def build_global_board(config, global_calender, jira_instance, bad_board=False):
    """
    Function to build our global boards for PMs.

    :param Dict config: Config Dict
    :param Dict global_calender: Calender starting with start date passed into config
    :param Dict jira_instance: JIRA instance to use
    :param Bool bad_board: Should we create the global bad board
    :return:
    """
    if bad_board:
        title = m.GLOBAL_BAD_BOARD
    else:
        title = m.GLOBAL_BOARD

    # Gets the default JIRA client to make the board
    if not jira_instance:
        jira_instance = config['SPU'].get('default_jira_instance', False)
    if not jira_instance:
        log.error("   No jira_instance for issue and there is no default in the config")
        raise Exception

    # Get the rest API client
    rest_api_client = JiraClient(
        url=config['SPU']['jira'][jira_instance['jira_instance']]['options']['server'],
        authtype='basic',
        username=config['SPU']['jira'][jira_instance['jira_instance']]['basic_auth'][0],
        password=config['SPU']['jira'][jira_instance['jira_instance']]['basic_auth'][1]
    )
    # Make 4 filters
    filters = []
    for quarter in range(1, 5):
        # Create our quarter label
        quarter_label = global_calender[quarter][0]['quarter_string']

        # Create our quarter filter
        quarter_filter = create_filter(
            quarters_label=quarter_label,
            project=f"{title} {jira_instance['jira_instance']} - {quarter_label}",
            rest_api_client=rest_api_client,
            glob=True)

        if bad_board:
            new_jql = f"(remainingEstimate > 0 OR duedate < endOfDay() " \
                f"OR status not in (Closed, Resolved) OR cf[11908] " \
                f"is not EMPTY) AND {quarter_filter['jql']}"
            rest_api_client.update_filter(
                name=quarter_filter['name'],
                jql=new_jql,
                filter_id=quarter_filter['id']
            )

        # Then create our quarter board
        new_board = rest_api_client.create_board(
            name=f"{title} {jira_instance['jira_instance']} - {quarter_label} Board",
            project=None,
            filter_id=int(quarter_filter['id']))
        # Add the filter to our list of filters
        filters.append(quarter_filter)
    return filters


def initial_global_jql(quarter_string, bad_board=False):
    """
    Helper function to return the initial global JQL query.

    :param String quarter_string: Quarter string to use
    :param Bool bad_board: Are we creating the JQL for the bad board
    :return: Initial JQL
    :rtype: String
    """
    if bad_board:
        return f"(remainingEstimate > 0 OR duedate < endOfDay() " \
            f"OR status not in (Closed, Resolved) OR cf[11908] " \
            f"is not EMPTY) AND labels = {quarter_string} ORDER BY Rank ASC"
    else:
        return f"labels = {quarter_string} ORDER BY Rank ASC"


def start_sync(calender, config, team, name, filters, bad_filters):
    """
    Function to start adding relevant information to JIRA.

    :param Dict calender: Calender dict
    :param Dict config: Config file
    :param Dict team: Team dict
    :param String name: Team name
    :param List filters: List of all global filters so we can append too
    :param List filters: List of all bad global filters so we can append too
    :return: Nothing
    """
    # Get our jira_instance we're using
    jira_instance = team.get('jira_instance', False)
    if not jira_instance:
        jira_instance = config['SPU'].get('default_jira_instance', False)
    if not jira_instance:
        log.warning("No JIRA instance can be found for %s" % name)

    # Get our JIRA client
    client = get_jira_client(team, config)
    # Get our Rest API JIRA client
    rest_api_client = JiraClient(
        url=config['SPU']['jira'][jira_instance]['options']['server'],
        authtype='basic',
        username=config['SPU']['jira'][jira_instance]['basic_auth'][0],
        password=config['SPU']['jira'][jira_instance]['basic_auth'][1]
    )
    # Get our project ID
    project_id = client.project(team['jira_project']).id

    for quarter, sprints in calender.items():
        if sprints:
            quarter_string = sprints[0]['quarter_string']
            # First create our filters
            quarter_filter = create_filter(
                quarters_label=quarter_string,
                project=team['jira_project'],
                rest_api_client=rest_api_client)

            # Update the share permission of that filter
            # TODO: Do we still need this?
            # rest_api_client.add_share_permissions(quarter_filter.id)

            # Now update the global filter board
            for fil in filters[jira_instance]:
                if sprints[0]['quarter_string'] in fil['name']:
                    # We found the filter we need to update
                    if team['jira_project'] not in fil['jql']:
                        if fil['jql'] == initial_global_jql(quarter_string):
                            # If this is the first project we're adding
                            new_jql = f"project = {team['jira_project']} AND {fil['jql']}"
                        else:
                            new_jql = f"project = {team['jira_project']} OR {fil['jql']}"
                        rest_api_client.update_filter(
                            name=fil['name'],
                            jql=new_jql,
                            filter_id=fil['id']
                        )

            for fil in bad_filters[jira_instance]:
                if sprints[0]['quarter_string'] in fil['name']:
                    # We found the filter we need to update
                    if team['jira_project'] not in fil['jql']: 
                        if fil['jql'] == initial_global_jql(quarter_string, bad_board=True):
                            # If this is the first project we're adding
                            new_jql = f"project = {team['jira_project']} AND {fil['jql']}"
                        else:
                            new_jql = f"project = {team['jira_project']} OR {fil['jql']}"
                        rest_api_client.update_filter(
                            name=fil['name'],
                            jql=new_jql,
                            filter_id=fil['id']
                        )

            # Then create a new board
            new_board = rest_api_client.create_board(
                name=f"{sprints[0]['quarter_string']} - {name} Board",
                project=team['jira_project'],
                filter_id=int(quarter_filter['id']))

            # Create a new issue using the new label
            kwargs = dict(
                project=dict(key=team['jira_project']),
                summary=f'Quarter {quarter} Issue',
                labels=[sprints[0]['quarter_string']],
                issuetype=dict(name='Story'),
            )
            new_issue = client.create_issue(**kwargs)

            # Now create our sprints
            sprints = create_sprints(new_board, sprints, client)



