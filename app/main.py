import sqlite3
import sys

from src.helpers import connect_to_db, show_help, start
from src.relative_service import (relative_list_all, relative_load,
                                  relative_modify, relative_new,
                                  relatives_show_all)
from src.visualize import generate_tree
from tabulate import tabulate

FEATURES = ("first_name", "last_name", "gender", "family_name",
            "date_of_birth", "place_of_birth", "date_of_death",
            "place_of_death", "phone", "email", "events", "desc",
            "spouse", "children")

ARGUMENTS = ("-h", "--help")

if __name__ == "__main__":

    for argument in sys.argv:
        if argument in ARGUMENTS:
            if argument in ["-h", "--help"]:
                show_help()
                break
        else:
            sys.exit("Error: wrong command line argument")

    try:
        db_connection = connect_to_db()

        while True:
            start_option = start()

            # 1. Add new person to database
            if start_option == 1:
                while True:
                    relative_new(db_connection)
                    another = input("Add another? [Y/N] ").strip().lower()
                    if another == "y":
                        pass
                    else:
                        break

            # 2. Modify existing person in database
            elif start_option == 2:

                first_name = input("Search for first name: ").strip()
                last_name = input("Search for last name: ").strip()

                # Search for list of matches
                relatives_loaded = relative_load(
                    db_connection, first_name=first_name, last_name=last_name)

                # If there are multiple people with the given name - list them
                found = len(relatives_loaded)
                if len(relatives_loaded) > 1:
                    for person in relatives_loaded:
                        list_item = (((len(relatives_loaded) + 1) - found), '. ', person.first_name,
                                     ' ', person.last_name, ', born ', person.date_of_birth)
                        print(str(list_item))
                        found -= 1

                    # Ask which entry to edit
                    person_choice = input("Which person to edit? ").strip()

                    # Person object to edit is:
                    person_to_edit = relatives_loaded[int(person_choice) - 1]

                # If there are none - exit
                elif relatives_loaded is None:
                    print("No such person in database")

                else:
                    person_to_edit = relatives_loaded[0]

                # Ask which info to edit
                info_to_edit = int(input("""Which info to add / edit:
1. Family name
2. Date of birth
3. Place of birth
4. Date of death
5. Place of death
6. Phone number
7. Email address
8. Events
9. Description
Proceed with: """).strip())

                # Ask with what content to edit
                new_content = input("Enter new info: ").strip()

                person_edited = relative_modify(
                    person_to_edit, info_to_edit, new_content)

                # Save to database with modified info
                try:
                    db_connection.execute("""INSERT INTO family (?)
                                            VALUES(?) WHERE first_name = ? AND last_name = ?""",
                                          info_to_edit,
                                          new_content,
                                          person_edited.first_name,
                                          person_edited.last_name)

                    print("Modified info (" + person_to_edit.first_name +
                          " " + person_to_edit.last_name + ") saved")

                except sqlite3.Error:
                    sys.exit("Error saving to database")
                except FileNotFoundError:
                    sys.exit("File not found")

            # 3. Generate tree
            elif start_option == 3:
                generate_tree()

            # 4. Print a list of all relatives
            elif start_option == 4:
                print(relatives_show_all(db_connection))

            # 5. Print a detailed list of all relatives
            elif start_option == 5:
                print(tabulate(relative_list_all(db_connection)))

            # 6. Exit
            elif start_option == 6:
                sys.exit()

            else:
                print("Wrong input")

    except (ValueError, TypeError):
        sys.exit("Input error")
    except sqlite3.Error:
        sys.exit("Error with database")