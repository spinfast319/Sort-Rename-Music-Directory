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
album_directory = "M:\Python Test Environment\Albums2"  # Which directory do you want to start with?
renamed_directory = "M:\Python Test Environment\Renamed2"  # Which directory do you want to copy the rename folders to?
log_directory = "M:\Python Test Environment\Logs"  # Which directory do you want the log in?
work_directory = "M:\Python Test Environment\Work"  # Create directory for temp file storage and renaming


# Set whether you are using nested folders or have all albums in one directory here
# If you have all your ablums in one music directory Music/Album_name then set this value to 1
# If you have all your albums nest in a Music/Artist/Album style of pattern set this value to 2
# The default is 1
album_depth = 1

"""
#  Set your linux directories here
album_directory = "/mnt/m/Python Test Environment/Albums" # Which directory has the albums you want to update the origin files for
renamed_directory = "/mnt/m/Python Test Environment/Renamed" # Which directory do you want to copy the rename folders to?
log_directory = "/mnt/m/Python Test Environment/Logs" # Which directory do you want the log albums that have missing origin files in?
work_directory = "/mnt/m/Python Test Environment/Work"  # Create directory for downloading the origin file to before you move it to the final directory.
"""

# Establishes the counters for completed albums and missing origin files
count = 0
good_missing = 0
bad_missing = 0
parse_error = 0
error_message = 0

# identifies location origin files are supposed to be
path_segments = album_directory.split(os.sep)
segments = len(path_segments)
origin_location = segments + album_depth

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


# A function to log events
def log_outcomes(d, p, m):
    global log_directory
    script_name = "Sort-Rename-Music-Directory Script"
    today = datetime.datetime.now()
    log_name = p
    directory = d
    message = m
    album_name = directory.split(os.sep)
    album_name = album_name[-1]
    log_path = log_directory + os.sep + log_name + ".txt"
    with open(log_path, "a", encoding="utf-8") as log_name:
        log_name.write("--{:%b, %d %Y}".format(today) + " at " + "{:%H:%M:%S}".format(today) + " from the " + script_name + ".\n")
        log_name.write("The album folder " + album_name + " " + message + ".\n")
        log_name.write("Album location: " + directory + "\n")
        log_name.write(" \n")
        log_name.close()


# A function that writes a summary of what the script did at the end of the process
def summary_text():
    global count
    global parse_error
    global bad_missing
    global good_missing
    global error_message

    print("")
    print("This script reorganized " + str(count) + " albums. You did the thing!")
    print("This script looks for potential missing files or errors. The following messages outline whether any were found.")
    if parse_error >= 1:
        print("--Warning: There were " + str(parse_error) + " albums skipped due to not being able to open the yaml. Redownload the yaml file.")
        error_message += 1  # variable will increment if statement is true
    elif parse_error == 0:
        print("--Info: There were " + str(parse_error) + " albums skipped due to not being able to open the yaml.")
    if bad_missing >= 1:
        print("--Warning: There were " + str(bad_missing) + " folders missing an origin files that should have had them.")
        error_message += 1  # variable will increment if statement is true
    elif bad_missing == 0:
        print("--Info: There were " + str(bad_missing) + " folders missing an origin files that should have had them.")
    if good_missing >= 1:
        print("--Info: Some folders didn't have origin files and probably shouldn't have origin files. " + str(good_missing) + " of these folders were identified.")
        error_message += 1  # variable will increment if statement is true
    elif good_missing == 0:
        print("--Info: Some folders didn't have origin files and probably shouldn't have origin files. " + str(good_missing) + " of these folders were identified.")
    if error_message >= 1:
        print("Check the logs to see which folders had errors and what they were.")
    else:
        print("There were no errors.")


#  A function that gets the directory and then opens the origin file and prints the name of the folder
def sort_rename(directory):
    global count
    global good_missing
    global bad_missing
    global parse_error
    global origin_location
    print("\n")
    print("Sorting and renaming " + directory)
    # check to see if there is an origin file
    file_exists = os.path.exists("origin.yaml")
    # if origin file exists, load it, copy, and rename
    if file_exists == True:
        # open the yaml
        try:
            with open(directory + os.sep + "origin.yaml", encoding="utf-8") as f:
                data = yaml.load(f, Loader=yaml.FullLoader)
        except:
            print("--There was an issue parsing the yaml file and the cover could not be downloaded.")
            print("----Logged missing cover due to parse error. Redownload origin file.")
            log_name = "parse-error"
            log_message = "had an error parsing the yaml and the cover art could not be downloaded. Redownload the origin file"
            log_outcomes(directory, log_name, log_message)
            parse_error += 1  # variable will increment every loop iteration
            return

        # turn the data into variables
        artist_name = data["Artist"]
        album_name = data["Name"]
        original_folder_name = data["Directory"]
        original_year = data["Original year"]
        edition = data["Edition"]
        catalog_number = data["Catalog number"]
        f.close()

        # check to see if a folder with the artist name exists
        clean_artist_name = cleanFilename(artist_name)
        clean_artist_folder_path = renamed_directory + os.sep + clean_artist_name
        isdir_artist = os.path.isdir(clean_artist_folder_path)

        # create artist folder if it doesn't exist
        if isdir_artist == True:
            print("--No new directory needed for " + artist_name)
        else:
            os.mkdir(clean_artist_folder_path)
            print("--Created directory for " + artist_name)

        # copy directory to work folder
        full_work_path = work_directory + os.sep + original_folder_name
        shutil.copytree(directory, full_work_path)
        print("--Copied " + original_folder_name + " to work directory")

        # check to see if an album with the name exists in the artist folder and try a variation if there is
        # start by setting up different folder names if there is a duplicate folder (normal>edition>catalog>original year)
        artist_album_path = clean_artist_folder_path + os.sep + album_name
        isdir_album = os.path.isdir(artist_album_path)
        artist_album_edition_path = clean_artist_folder_path + os.sep + album_name + " (" + str(edition) + ")"
        isdir_album_edition = os.path.isdir(artist_album_edition_path)
        artist_album_catalog_path = clean_artist_folder_path + os.sep + album_name + " (Cat# " + str(catalog_number) + ")"
        isdir_album_catalog = os.path.isdir(artist_album_catalog_path)
        artist_album_year_path = clean_artist_folder_path + os.sep + album_name + " (" + str(original_year) + ")"
        isdir_album_year = os.path.isdir(artist_album_year_path)
        # set album_name for folder based on wheter there is an existing folder and the right metadata
        if isdir_album == False:
            print("--There is no folder called " + album_name + ". Rename and move the album.")
            final_album_name = album_name
        elif isdir_album_edition == False and edition != None:
            print("--There is no folder called " + album_name + " (" + str(edition) + ". Rename and move the album.")
            final_album_name = album_name + " (" + str(edition) + ")"
        elif isdir_album_catalog == False and catalog_number != None:
            print("--There is no folder called " + album_name + " (Cat# " + str(catalog_number) + ". Rename and move the album.")
            final_album_name = album_name + " (Cat# " + str(catalog_number) + ")"
        elif isdir_album_year == False and original_year != None:
            print("--There is no folder called " + album_name + " (" + str(original_year) + ". Rename and move the album.")
            final_album_name = album_name + " (" + str(original_year) + ")"

        # run windows string cleaning function to remove illegal characters
        # calls the function cleanFilename feeding it the final album name and creating new cleaned variable
        clean_final_album_name = cleanFilename(final_album_name)

        # rename album folder
        final_album_path = work_directory + os.sep + clean_final_album_name
        os.rename(full_work_path, final_album_path)
        print("--Renamed " + original_folder_name + " to " + clean_final_album_name)

        # move renamed album to artist folder
        full_artist_folder_path = clean_artist_folder_path + os.sep + clean_final_album_name
        shutil.move(final_album_path, full_artist_folder_path)
        print("--Moved " + clean_final_album_name + " to " + artist_name + " directory")

        count += 1  # variable will increment every loop iteration
    # otherwise log that the origin file is missing
    else:
        # split the director to make sure that it distinguishes between foldrs that should and shouldn't have origin files
        current_path_segments = directory.split(os.sep)
        current_segments = len(current_path_segments)
        # create different log files depending on whether the origin file is missing somewhere it shouldn't be
        if origin_location != current_segments:
            # log the missing origin file folders that are likely supposed to be missing
            print("--An origin file is missing from a folder that should not have one.")
            print("--Logged missing origin file.")
            log_name = "good-missing-origin"
            log_message = "origin file is missing from a folder that should not have one.\nSince it shouldn't be there it is probably fine but you can double check"
            log_outcomes(directory, log_name, log_message)
            good_missing += 1  # variable will increment every loop iteration
        else:
            # log the missing origin file folders that are not likely supposed to be missing
            print("--An origin file is missing from a folder that should have one.")
            print("--Logged missing origin file.")
            log_name = "bad-missing-origin"
            log_message = "origin file is missing from a folder that should have one"
            log_outcomes(directory, log_name, log_message)
            bad_missing += 1  # variable will increment every loop iteration


# The main function that controls the flow of the script
def main():

    # intro text
    print("")
    print("Zhu Li, do the thing!")

    try:
        # Get all the subdirectories of album_directory recursively and store them in a list:
        directories = [os.path.abspath(x[0]) for x in os.walk(album_directory)]
        directories.remove(os.path.abspath(album_directory))  # If you don't want your main directory included

        #  Run a loop that goes into each directory identified in the list and runs the function that copies and renames the folders
        for i in directories:
            os.chdir(i)  # Change working Directory
            sort_rename(i)  # Run your function

    finally:
        # run summary text function to provide error messages
        summary_text()


if __name__ == "__main__":
    main()


# Future idea
# Add error handling album already exists-skip and log
