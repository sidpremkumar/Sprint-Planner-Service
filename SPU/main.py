"""
This is the main module used to start the utility.
"""
# Build in Modules
from datetime import datetime, timedelta
import logging

# Local Modules
from config import config
import SPU.downstream as d

# Global Variables
GLOBAL_BOARD = 'GLOBAL_BOARD'
GLOBAL_BAD_BOARD = 'GLOBAL_BAD_BOARD'
log = logging.getLogger(__name__)

def load_config():
    """
    Helper function to load in config file

    :return: Config File
    :rtype: Dict
    """
    return config


def build_sprint(operational_year, operational_quarter, sprint_length, sprint_index):
    """
    Helper function to build Sprint name for JIRA.

    :param String operational_year:
    :param String operational_quarter:
    :param String sprint_length:
    :param String sprint_index:
    :return: Formatted Sprint name
    :rtype: String
    """
    return 'Y%s-Q%s-L%s-S%s' % (
        operational_year, operational_quarter, sprint_length, sprint_index
    )


def build_quarter_string(operational_year, operational_quarter):
    """
    Helper function to build quarter name for JIRA.

    :param String operational_year:
    :param String operational_quarter:
    :return: Formatted Quarter name
    :rtype: String
    """
    return 'Y%s-Q%s' % (operational_year, operational_quarter)


def build_calender(global_start, start_date, sprint_length):
    """
    Build a Dict of quarters based on the Q1 Start date.

    :param String global_start: Global start date
    :param String start_date: Start date in 'MM-DD' format
    :param Int sprint_length: Length of a sprint per team
    :return: Calender Dict of all start and end dates
    :rtype: Dict
    """
    # First convert our values to datetime
    global_start_datetime = datetime.strptime(global_start, '%m-%d-%y')
    sprint_start_datetime = datetime.strptime(start_date, '%m-%d-%y')
    current_datetime = sprint_start_datetime
    current_year = current_datetime.year - 2000
    calender = {}
    index = 1

    if sprint_length == 2:
        # Validate sprint start date
        if not global_start_datetime - timedelta(weeks=1) <= sprint_start_datetime \
                 <= global_start_datetime + timedelta(weeks=1):
            log.warning('Invalid Sprint start time. 2 week sprints must be within 1 week of the Q1 start date')
            raise ValueError
        for year in range(1, 10):
            for quarter in range(1, 5):
                # We have 4 quarters
                quarter_calender = []
                for sprint_index in range(1, 7):
                    # If our sprint length is 2, we need 6 sprints per quarter
                    if (current_datetime - sprint_start_datetime).days >= 14:
                        # Every two week change the sprint_start_datetime
                        sprint_start_datetime += timedelta(weeks=2)

                    new_entry = dict(
                        index=sprint_index,
                        quarter=quarter,
                        start_date=current_datetime,
                        end_date=(current_datetime + timedelta(weeks=2)),
                        sprint_string=build_sprint(
                            operational_year=current_year,
                            operational_quarter=quarter,
                            sprint_length=sprint_length,
                            sprint_index=sprint_index

                        ),
                        quarter_string=build_quarter_string(
                            operational_quarter=quarter,
                            operational_year=current_datetime.year-2000
                        ),
                    )

                    # Add our entry to the calender
                    quarter_calender.append(new_entry)

                    # Move 2 weeks in the future
                    current_datetime += timedelta(weeks=2)
                # Add our quarter calender to the calender
                calender[index] = quarter_calender
                index += 1
            current_year += 1

        # Adding 13th week every quarter
        current_datetime += timedelta(weeks=1)

    elif sprint_length == 3:
        # Validate sprint start date
        if not global_start_datetime - timedelta(days=10) <= sprint_start_datetime  \
                <= global_start_datetime + timedelta(days=10):
            log.warning('Invalid Sprint start time. 3 week sprints must be within 10 days of the Q1 start date')
            raise ValueError
        for year in range(1, 10):
            for quarter in range(1, 5):
                # We have 4 quarters
                quarter_calender = []
                for sprint_index in range(1, 4):
                    # If our sprint length is 3, we need 3 sprints per quarter
                    if (current_datetime - sprint_start_datetime).days >= 14:
                        # Every two week change the sprint_start_datetime
                        sprint_start_datetime += timedelta(weeks=2)

                    new_entry = dict(
                        index=sprint_index,
                        quarter=quarter,
                        start_date=current_datetime,
                        end_date=(current_datetime + timedelta(weeks=2)),
                        sprint_string=build_sprint(
                            operational_year=current_datetime.year-2000,
                            operational_quarter=quarter,
                            sprint_length=sprint_length,
                            sprint_index=sprint_index

                        ),
                        quarter_string=build_quarter_string(
                            operational_quarter=quarter,
                            operational_year=current_datetime.year-2000
                        ),
                    )

                    # Add our entry to the calender
                    quarter_calender.append(new_entry)
                    index += 1

                    # Move 3 weeks in the future
                    current_datetime += timedelta(weeks=3)
                # Add our quarter calender to the calender
                calender[index] = quarter_calender
                index += 1

            # Adding 13th week every quarter
            current_datetime += timedelta(weeks=1)

    # Return our calender
    return calender


def validate_team(all_borads, calender, team, glob=False):
    """
    Helper function to validate if a team should be synced or not.

    :param Dict all_borads: All boards
    :param Dict calender: Calender created for the team
    :param String team: Team name
    :param Bool glob: Are we checking for the global board
    :return: True/False if the team should be synced
    :rtype: Bool
    """
    # Gather all quarters
    quarters = []
    for quarter, value in calender.items():
        if value:
            if value[0]['quarter_string'] not in quarters:
                quarters.append(value[0]['quarter_string'])

    if not glob:
        # Check if the boards are in JIRA already
        for quarter in quarters:
            if f'{quarter} - {team} Board' in all_borads.keys():
                return False
        return True
    else:
        # Check if the boards are in JIRA already
        for quarter in quarters:
            if f'{team} - {quarter} Board' in all_borads.keys():
                return False
        return True


def prompt_user(calender, type):
    """
    Prompt the user with what will be created on JIRA.

    :param Dict calender: The calender to verify
    :param String type: What type of calender is this
    """
    print('SPS will create the following Quarters and Sprints')
    if len(calender.keys()) > 4:
        bound = 5
    else:
        bound = len(calender.keys()) + 1
    for quarter in range(1, bound):
        print(f"* Quarter: {calender[quarter][0]['quarter_string']}")
        for sprint in calender[quarter]:
            print(f"\t {sprint['sprint_string']}")
    print(f'Is this valid for {type}?')
    answer = None
    while answer not in ("yes", "no"):
        answer = input("Enter yes or no: ")
        if answer == "yes":
            return
        elif answer == "no":
            print('Exiting utility...')
            exit()
        else:
            print("Please enter yes or no.")


def main():
    """
    Function to read config file and start service.
    """
    config = load_config()
    global_start_date = config['SPU']['operational_q1_start']

    # First get all our boards so we can validate teams
    all_teams = []
    for name, jira in config['SPU']['jira'].items():
        # Append it to a list of jiras
        new_entry = {'jira_instance': name}
        if new_entry not in all_teams:
            all_teams.append(new_entry)

    # Now get all boards associated with all teams
    all_boards = d.get_boards(config, all_teams)

    # Loop through all JIRA instances and check if
    # They have a global board
    filters = {}
    bad_filters = {}
    global_calender = build_calender(global_start_date, global_start_date, 2)

    for jira in all_teams:
        # Check the global board
        build_global_board = validate_team(all_boards,
                                           global_calender,
                                           f"{GLOBAL_BOARD} {jira['jira_instance']}",
                                           glob=True)

        if build_global_board:
            # Prompt our user
            prompt_user(global_calender, GLOBAL_BOARD)
            # Build our our global board for the JIRA instance
            filter_resp = d.build_global_board(config, global_calender, jira)
            filters[jira['jira_instance']] = filter_resp
        else:
            # We just need to get the filters
            filter_resp = d.get_global_filters(jira, config)
            filters[jira['jira_instance']] = filter_resp

        # Check the bad board
        build_global_bad_board = validate_team(all_boards,
                                               global_calender,
                                               f"{GLOBAL_BAD_BOARD} {jira['jira_instance']}",
                                               glob=True)
        if build_global_bad_board:
            # Prompt our user
            prompt_user(global_calender, GLOBAL_BAD_BOARD)
            # Build out global bad board for the JIRA issue
            filter_resp = d.build_global_board(config, global_calender, jira, bad_board=True)
            bad_filters[jira['jira_instance']] = filter_resp
        else:
            # We just need to get the filters
            filter_resp = d.get_global_filters(jira, config, bad_board=True)
            bad_filters[jira['jira_instance']] = filter_resp

    for team, value in config['SPU']['teams'].items():
        # Build our calender
        calender = build_calender(global_start_date, value['sprint_start_date'], value['sprint_length'])

        if not config['SPU']['run_for_quarter']:
            # Only run for the next 4 quarters
            calender = {1: calender[1], 2: calender[2], 3: calender[3], 4: calender[4]}
            # Check if the boards already exist
            if validate_team(all_boards, calender, team):
                # Prompt our user
                prompt_user(calender, team)
                # Now add relevant information downstream
                d.start_sync(
                    calender=calender,
                    config=config,
                    team=value,
                    name=team,
                    filters=filters,
                    bad_filters=bad_filters
                )
        else:
            # Else we need to only run for a specific quarter
            # First find the quarter
            for index, quarter in calender.items():
                if quarter[0]['quarter_string'] == config['SPU']['run_for_quarter']:
                    calender = {1: quarter}
                    break
            if validate_team(all_boards, calender, team):
                # Prompt our user
                prompt_user(calender, team)
                # Now add relevant information downstream
                d.start_sync(
                    calender=calender,
                    config=config,
                    team=value,
                    name=team,
                    filters=filters,
                    bad_filters=bad_filters
                )


if __name__ == '__main__':
    main()
