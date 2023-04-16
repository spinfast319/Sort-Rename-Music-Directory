# Sort and Rename Music Directories
# author: hypermodified
# This script is meant to use yaml origin files to provide standardised metadata to rename music folders
# It takes the folder and reads what the artist and album name are. It then creates a artist folder and then renames the album to just the album name and moves it into the folder.
# It can handle albums with artwork folders or multiple disc folders in them. It can also handle specials characters and removes any characters that makes windows fail.
# It can also handle multiple versions of the same album. If it finds a folder already exists with the album name it will rename it with additional metadata.
# It starts with adding the edition if it has one, then it tries the catalog number, then the year. It will fail if versions with those already exists but that could be extended if needed.
# It has been tested and works in both Ubuntu Linux and Windows 10.

# Import dependencies
import os  # Imports functionality that let's you interact with your operating system
import yaml  # Imports yaml
import shutil  # Imports functionality that lets you copy files and directory
import datetime  # Imports functionality that lets you make timestamps


#  Set your directories here
album_directory = "M:\Python Test Environment\Albums"  # Which directory do you want to start with?
renamed_directory = "M:\Python Test Environment\Music"  # Which directory do you want to copy the rename folders to?
log_directory = "M:\Python Test Environment\Logs"  # Which directory do you want the log in?
work_directory = "M:\Python Test Environment\Work"  # Create directory for temp file storage and renaming


# Set whether you are using nested folders or have all albums in one directory here
# If you have all your ablums in one music directory Music/Album_name then set this value to 1
# If you have all your albums nest in a Music/Artist/Album style of pattern set this value to 2
# The default is 1
album_depth = 1

# Establishes the counters for completed albums and missing origin files
count = 0
good_missing = 0
bad_missing = 0
parse_error = 0
origin_old = 0
error_message = 0
total_count = 0
remove_count = 0

# identifies location origin files are supposed to be and sets album_name
path_segments = album_directory.split(os.sep)
segments = len(path_segments)
# origin_location = segments + album_depth
album_location_check = segments + album_depth

# creates the list of albums that will be removed post sorting, renaming and moving
remove_set = set()

# A function to log events
def log_outcomes(directory, log_name, message):
    global log_directory

    script_name = "Sort-Rename-Music-Directory Script"
    today = datetime.datetime.now()
    log_name = f"{log_name}.txt"
    album_name = directory.split(os.sep)
    album_name = album_name[-1]
    log_path = os.path.join(log_directory, log_name)
    with open(log_path, "a", encoding="utf-8") as log_name:
        log_name.write(f"--{today:%b, %d %Y} at {today:%H:%M:%S} from the {script_name}.\n")
        log_name.write(f"The album folder {album_name} {message}.\n")
        log_name.write(f"Album location: {directory}\n")
        log_name.write(" \n")
        log_name.close()


# A function that determines if there is an error
def error_exists(error_type):
    global error_message

    if error_type >= 1:
        error_message += 1  # variable will increment if statement is true
        return "Warning"
    else:
        return "Info"


# A function that writes a summary of what the script did at the end of the process
def summary_text():
    global count
    global parse_error
    global bad_missing
    global good_missing
    global origin_old
    global error_message
    global total_count
    global remove_count

    print("")
    print(f"This script reorganized {count} albums out of {total_count}. After moving and renaming them it removed {remove_count} albums.")
    print("This script looks for potential missing files or errors. The following messages outline whether any were found.")

    error_status = error_exists(parse_error)
    print(f"--{error_status}: There were {parse_error} albums skipped due to not being able to open the yaml. Redownload the yaml file.")
    error_status = error_exists(origin_old)
    print(f"--{error_status}: There were {origin_old} origin files that do not have the needed metadata and need to be updated.")
    error_status = error_exists(bad_missing)
    print(f"--{error_status}: There were {bad_missing} folders missing an origin files that should have had them.")
    error_status = error_exists(good_missing)
    print(f"--Info: Some folders didn't have origin files and probably shouldn't have origin files. {good_missing} of these folders were identified.")

    if error_message >= 1:
        print("Check the logs to see which folders had errors and what they were.")
    else:
        print("There were no errors.")


#  A function to replace illegal characters in the windows operating system
#  For other operating systems you could tweak this for their illegal characters
def cleanFilename(file_name):
    if not file_name:
        return ""
    badchar1 = '"'
    badchar2 = "?"
    badchar3 = ":"
    badchar4 = "*"
    badchar5 = "|"
    badchar6 = "<"
    badchar7 = ">"
    badchar8 = "\\"
    badchar9 = "/"
    for c in badchar1:
        file_name = file_name.replace(c, "＂")
    for c in badchar2:
        file_name = file_name.replace(c, "？")
    for c in badchar3:
        file_name = file_name.replace(c, "：")
    for c in badchar4:
        file_name = file_name.replace(c, "＊")
    for c in badchar5:
        file_name = file_name.replace(c, "｜")
    for c in badchar6:
        file_name = file_name.replace(c, "＜")
    for c in badchar7:
        file_name = file_name.replace(c, "＞")
    for c in badchar8:
        file_name = file_name.replace(c, "＼")
    for c in badchar9:
        file_name = file_name.replace(c, "／")
    return file_name


# A function to remove the original albums that were copied and renamed
def remove_albums(remove_set):
    global remove_count

    # Loop through the list of albums to remove
    for i in remove_set:

        # Break each entry into a source and target
        original_path = i[0]
        new_path = i[1]

        # Remove them
        print("")
        print("Removing.")
        print(f"--Removed: {original_path}")
        print(f"--New Location: {new_path}")
        shutil.rmtree(original_path)
        remove_count += 1  # variable will increment every loop iteration


# A function to check if the origin file is there and to determine whether it is supposed to be there.
def check_file(directory):
    global good_missing
    global bad_missing
    global album_location_check
    global total_count

    # get the depth of this directory
    current_path_segments = directory.split(os.sep)
    current_segments = len(current_path_segments)

    # check to see if this is an album and count it if it is
    if album_location_check == current_segments:
        total_count += 1  # variable will increment every loop iteration

    # check to see if there is an origin file
    file_exists = os.path.exists("origin.yaml")
    # if origin file exists, load it, copy, and rename
    if file_exists == True:
        return True
    else:
        # split the directory to make sure that it distinguishes between folders that should and shouldn't have origin files
        # create different log files depending on whether the origin file is missing somewhere it shouldn't be
        if album_location_check != current_segments:
            # log the missing origin file folders that are likely supposed to be missing
            print("--An origin file is missing from a folder that should not have one.")
            print("--Logged missing origin file.")
            log_name = "good-missing-origin"
            log_message = "origin file is missing from a folder that should not have one.\nSince it shouldn't be there it is probably fine but you can double check"
            log_outcomes(directory, log_name, log_message)
            good_missing += 1  # variable will increment every loop iteration
            return False
        else:
            # log the missing origin file folders that are not likely supposed to be missing
            print("--An origin file is missing from a folder that should have one.")
            print("--Logged missing origin file.")
            log_name = "bad-missing-origin"
            log_message = "origin file is missing from a folder that should have one"
            log_outcomes(directory, log_name, log_message)
            bad_missing += 1  # variable will increment every loop iteration
            return False


#  A function that gets the directory and then opens the origin file and extracts the needed variables
def get_metadata(directory):
    global parse_error
    global origin_old
    global bad_missing

    # check to see if there is an origin file
    file_exists = os.path.exists("origin.yaml")
    origin_location = os.path.join(directory, "origin.yaml")
    # if origin file exists, load it, copy, and rename
    if file_exists == True:
        print("--The origin file location is valid.")
        # get album name
        album_name = directory.split(os.sep)
        album_name = album_name[-1]
        print(f"--Getting metadata for {album_name}")
        # open the yaml
        try:
            with open(origin_location, encoding="utf-8") as f:
                data = yaml.load(f, Loader=yaml.FullLoader)
        except:
            print("--There was an issue parsing the yaml file and the cover could not be downloaded.")
            print("--Logged missing cover due to parse error. Redownload origin file.")
            log_name = "parse-error"
            log_message = "had an error parsing the yaml and the cover art could not be downloaded. Redownload the origin file"
            log_outcomes(directory, log_name, log_message)
            parse_error += 1  # variable will increment every loop iteration
            return
        # check to see if the origin file has the corect metadata
        if "Cover" in data.keys():
            print("--You are using the correct version of gazelle-origin.")

            # turn the data into variables
            origin_metadata = {
                "artist_name": data["Artist"],
                "album_name": data["Name"],
                "release_type": data["Release type"],
                "edition": data["Edition"],
                "edition_label": data["Record label"],
                "edition_cat": data["Catalog number"],
                "edition_year": data["Edition year"],
                "djs": data["DJs"],
                "composers": data["Composers"],
                "conductors": data["Conductors"],
                "original_year": data["Original year"],
                "media": data["Media"],
                "dl_directory": data["Directory"],
            }
            f.close()
            return origin_metadata
        else:
            print("--You need to update your origin files with more metadata.")
            print("--Switch to the gazelle-origin fork here: https://github.com/spinfast319/gazelle-origin")
            print("--Then run: https://github.com/spinfast319/Update-Gazelle-Origin-Files")
            print("--Then try this script again.")
            print("--Logged out of date origin file.")
            log_name = "out-of-date-origin"
            log_message = "origin file out of date"
            log_outcomes(directory, log_name, log_message)
            origin_old += 1  # variable will increment every loop iteration
    else:
        # log the missing origin file folders that are not likely supposed to be missing
        print("--An origin file is missing from a folder that should have one.")
        print("--Logged missing origin file.")
        log_name = "bad-missing-origin"
        log_message = "origin file is missing from a folder that should have one"
        log_list = None
        log_outcomes(directory, log_name, log_message, log_list)
        bad_missing += 1  # variable will increment every loop iteration


#  A function that gets the directory and then opens the origin file and creates a dict of metadata
def sort_rename(directory, origin_metadata):
    global count
    global remove_set
    global work_directory

    # turn the data into variables
    artist_name = origin_metadata["artist_name"]
    album_name = origin_metadata["album_name"]
    original_folder_name = origin_metadata["dl_directory"]
    original_year = origin_metadata["original_year"]
    edition = origin_metadata["edition"]
    catalog_number = origin_metadata["edition_cat"]

    # create dj variable
    if origin_metadata["djs"] != None:
        dj = origin_metadata["djs"]
        clean_dj_name = cleanFilename(dj)
    else:
        dj = None

    # set up artist, Various Artist, or DJ path
    clean_artist_name = cleanFilename(artist_name)
    if clean_artist_name == "Various Artists" and dj != None:
        clean_artist_folder_path = os.path.join(renamed_directory, clean_dj_name)
        dj_album = True
    else:
        clean_artist_folder_path = os.path.join(renamed_directory, clean_artist_name)
        dj_album = False

    # check to see if a folder with the artist name exists
    isdir_artist = os.path.isdir(clean_artist_folder_path)

    # create artist folder if it doesn't exist
    if isdir_artist == True:
        if dj_album == True:
            print(f"--No new directory needed for {clean_dj_name}")
        else:
            print(f"--No new directory needed for {clean_artist_name}")
    else:
        os.mkdir(clean_artist_folder_path)
        if dj_album == True:
            print(f"--Created directory for {clean_dj_name}")
        else:
            print(f"--Created directory for {clean_artist_name}")

    # strip invisible characters out of names
    original_folder_name = original_folder_name.strip()
    directory = directory.strip()

    # copy directory to work folder
    full_work_path = os.path.join(work_directory, original_folder_name)
    shutil.copytree(directory, full_work_path)
    print(f"--Copied {original_folder_name} to work directory")

    # check to see if an album with the name exists in the artist folder and try a variation if there is
    # start by setting up different folder names if there is a duplicate folder (normal>edition>catalog>original year)
    artist_album_path = os.path.join(clean_artist_folder_path, album_name)
    isdir_album = os.path.isdir(artist_album_path)
    artist_album_edition_path = clean_artist_folder_path + os.sep + album_name + " (" + str(edition) + ")"
    isdir_album_edition = os.path.isdir(artist_album_edition_path)
    artist_album_catalog_path = clean_artist_folder_path + os.sep + album_name + " (Cat# " + str(catalog_number) + ")"
    isdir_album_catalog = os.path.isdir(artist_album_catalog_path)
    artist_album_year_path = clean_artist_folder_path + os.sep + album_name + " (" + str(original_year) + ")"
    isdir_album_year = os.path.isdir(artist_album_year_path)
    # set album_name for folder based on wheter there is an existing folder and the right metadata
    if isdir_album == False:
        print(f"--There is no folder called {album_name}. Rename and move the album.")
        final_album_name = album_name
    elif isdir_album_edition == False and edition != None:
        print(f"--There is no folder called {album_name} ({edition}). Rename and move the album.")
        final_album_name = album_name + " (" + str(edition) + ")"
    elif isdir_album_catalog == False and catalog_number != None:
        print(f"--There is no folder called {album_name} (Cat# {catalog_number}). Rename and move the album.")
        final_album_name = album_name + " (Cat# " + str(catalog_number) + ")"
    elif isdir_album_year == False and original_year != None:
        print(f"--There is no folder called {album_name} ({original_year}). Rename and move the album.")
        final_album_name = album_name + " (" + str(original_year) + ")"

    # run windows string cleaning function to remove illegal characters
    # calls the function cleanFilename feeding it the final album name and creating new cleaned variable
    clean_final_album_name = cleanFilename(final_album_name)

    # rename album folder
    final_album_path = os.path.join(work_directory, clean_final_album_name)
    os.rename(full_work_path, final_album_path)
    print(f"--Renamed {original_folder_name} to {clean_final_album_name}")

    # move renamed album to artist folder
    full_artist_folder_path = os.path.join(clean_artist_folder_path, clean_final_album_name)
    shutil.move(final_album_path, full_artist_folder_path)
    if dj_album == True:
        print(f"--Moved {clean_final_album_name} to {clean_dj_name} directory")
    else:
        print(f"--Moved {clean_final_album_name} to {artist_name} directory")

    # remove original directory
    # make the pair a tupple
    remove_pair = (directory, full_artist_folder_path)
    # adds the tupple to the set
    remove_set.add(remove_pair)

    count += 1  # variable will increment every loop iteration
    return remove_set


# The main function that controls the flow of the script
def main():

    # intro text
    print("")
    print("Zhu Li, do the thing!")

    try:
        # Get all the subdirectories of album_directory recursively and store them in a list:
        directories = [os.path.abspath(x[0]) for x in os.walk(album_directory)]
        directories.remove(os.path.abspath(album_directory))  # If you don't want your main directory included

        print("")
        print("Part 1: Sort and Rename")

        #  Run a loop that goes into each directory identified in the list and runs the function that copies and renames the folders
        for i in directories:
            os.chdir(i)  # Change working Directory
            print("\n")
            print(f"Sorting and renaming {i}")
            origin_exists = check_file(i)  # Determine if folder should have origin file and if it does
            if origin_exists == True:
                origin_metadata = get_metadata(i)  # Get metadata associate with album
                if origin_metadata != None:
                    remove_set = sort_rename(i, origin_metadata)  # Sort and renam the album

        # Change directory so the album directory can be moved and move them
        os.chdir(log_directory)

        # Remove all of the albums that have been copied and renamed
        print("")
        print("Part 2: Clean Up")
        remove_albums(remove_set)

    finally:
        # run summary text function to provide error messages
        print("")
        print("You did the thing!")
        summary_text()


if __name__ == "__main__":
    main()


# Future idea
# Add error handling album already exists-skip and log
