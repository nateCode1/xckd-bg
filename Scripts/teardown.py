import datetime
import win32com.client
import os
import json


def remove_event():
    scheduler = win32com.client.Dispatch('Schedule.Service')
    scheduler.Connect()
    root_folder = scheduler.GetFolder('\\')

    try:
        # Attempt to delete the task if it exists
        root_folder.DeleteTask('Xkcd Bg Update', 0)
        print("Task successfully removed.")
    except Exception as e:
        print(f"Error removing task: {str(e)}")
        print("You can complete the uninstall manually by opening task scheduler and deleting the 'XKCD Bg Update' task.")


if __name__ == "__main__":
    remove_event()