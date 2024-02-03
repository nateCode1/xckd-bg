import datetime
import win32com.client
import os
import json


def setup_event():
    with open("../Data/config.json", 'r') as file:
        config = json.load(file)

    scheduler = win32com.client.Dispatch('Schedule.Service')
    scheduler.Connect()
    root_folder = scheduler.GetFolder('\\')
    task_def = scheduler.NewTask(0)

    # Create trigger
    if config["run"] == "Run Every x Hours":
        start_time = datetime.datetime.now() + datetime.timedelta(seconds=10)
        TASK_TRIGGER_TIME = 1
        trigger = task_def.Triggers.Create(TASK_TRIGGER_TIME)
        trigger.StartBoundary = start_time.isoformat()

        # Repeat forever*
        repetition = trigger.Repetition
        interval_hours = int(config.get("run_interval", 4))
        repetition.Interval = f"PT{interval_hours}H"  # Repeat every specified number of hours

    else:
        TASK_TRIGGER_LOGON = 9
        trigger = task_def.Triggers.Create(TASK_TRIGGER_LOGON)
        trigger.Id = "LogonTriggerId"
        trigger.UserId = os.environ.get('USERNAME') # current user account

    # Create action
    TASK_ACTION_EXEC = 0
    action = task_def.Actions.Create(TASK_ACTION_EXEC)
    action.ID = 'DO NOTHING'
    action.Path = 'cmd.exe'
    action.Arguments = '/c start /min "" ' + os.path.abspath('update.bat') + ' ^&exit'

    # Create update.bat file
    with open('update.bat', 'w') as bat_file:
        bat_file.write("cd " + os.path.abspath('main.py')[:-7] + '\n' + "Python main.py")

    # Set parameters
    task_def.RegistrationInfo.Description = 'Update the desktop background (from xkcd background manager).'
    task_def.Settings.Enabled = True
    task_def.Settings.StopIfGoingOnBatteries = False
    task_def.Settings.DisallowStartIfOnBatteries = False

    # Register task
    # If task already exists, it will be updated
    TASK_CREATE_OR_UPDATE = 6
    TASK_LOGON_NONE = 0
    root_folder.RegisterTaskDefinition(
        'Xkcd Bg Update',  # Task name
        task_def,
        TASK_CREATE_OR_UPDATE,
        '',  # No user
        '',  # No password
        TASK_LOGON_NONE)


if __name__ == "__main__":
    setup_event()