# Sort and Rename Music Directories
# author: hypermodified
# version: 1.0
# This script is meant to use yaml origin files to provide standardised metadata to rename music folders
# It takes the folder and reads what the artist and album name are. It then creates a artist folder and then renames the album to just the album name and moves it into the folder.
# It can handle albums with artwork folders or multiple disc folders in them. It can also handle specials characters and removes any characters that makes windows fail.
# It can also handle multiple versions of the same album. If it finds a folder already exists with the album name it will rename it with additional metadata.
# It starts with adding the edition if it has one, then it tries the catalog number, then the year. It will fail if versions with those already exists but that could be extended if needed.
#test

# Import dependencies
import os  # Imports functionality that let's you interact with your operating system
import yaml  # Imports yaml
import shutil # Imports functionality that lets you copy files and directory
import datetime # Imports functionality that lets you make timestamps

#  Set your directories here
directory_to_check = "M:\Python Test Environment\Albums" # Which directory do you want to start with?
renamed_directory = "M:\Python Test Environment\Renamed" # Which directory do you want to copy the rename folders to?
log_directory = "M:\Python Test Environment\Logs" # Which directory do you want the log in?
work_directory = "M:\Python Test Environment\Work" # Create directory for temp file storage and renaming

# Set up the counters for completed albums and missing origin files
count = 0
missing = 0

#intro text
print("")
print("Zhu Li, do the thing!")
print("")

#  A function to replace illegal characters in the windows operating system
#  For other operating systems you could tweak this for their illegal characters
def cleanFilename(s):
    if not s:
        return ''
    badchars = '\\/:*\"<>|'
    badchars2 = '?'
    for c in badchars:
        s = s.replace(c, '-')
    return s; 
    #for c in badchars2:
    #    s = s.replace(c, '？')
    #return s; 



#  A function that gets the directory and then opens the origin file and prints the name of the folder
def sort_rename(directory):
        global count
        global missing
        print("Sorting and renaming " + directory)
        #check to see if there is an origin file
        file_exists = os.path.exists('origin.yaml')
        #if origin file exists, load it, copy, and rename
        if file_exists == True:
            #open the yaml and turn the data into variables
            with open(directory + '\origin.yaml',encoding='utf-8') as f:
              data = yaml.load(f, Loader=yaml.FullLoader)
            artist_name = data['Artist']    
            album_name =  data['Name']
            original_folder_name = data['Directory'] 
            original_year = data['Original year']
            edition = data['Edition']
            catalog_number = data['Catalog number']
                        
            #check to see if a folder with the artist name exists
            artist_folder_path = renamed_directory + "\\" + artist_name  
            isdir_artist = os.path.isdir(artist_folder_path)   
            
            #create artist folder if it doesn't exist
            if isdir_artist == True:
                print ("--No new directory needed for " + artist_name)
            else:
                os.mkdir(artist_folder_path)
                print ("--Created directory for " + artist_name)
                
            #copy directory to work folder   
            full_work_path = work_directory + "\\" + original_folder_name
            shutil.copytree(directory, full_work_path)  
            print ("--Copied " + original_folder_name + " to work directory")   
         
           #check to see if an album with the name exists in the artist folder and try a variation if there is 
           #start by setting up different folder names if there is a duplicate folder (normal>edition>catalog>original year)
            artist_album_path = artist_folder_path + "\\" + album_name  
            isdir_album = os.path.isdir(artist_album_path)   
            artist_album_edition_path = artist_folder_path + "\\" + album_name + " (" + str(edition) + ")"  
            isdir_album_edition = os.path.isdir(artist_album_edition_path) 
            artist_album_catalog_path = artist_folder_path + "\\" + album_name + " (Cat# " + str(catalog_number) + ")"  
            isdir_album_catalog = os.path.isdir(artist_album_catalog_path)
            artist_album_year_path = artist_folder_path + "\\" + album_name + " (" + str(original_year) + ")"  
            isdir_album_year = os.path.isdir(artist_album_year_path)
            #set album_name for folder based on wheter there is an existing folder and the right metadata
            if isdir_album == False:
                print ("--There is no folder called " + album_name + ". Rename and move the album.")
                final_album_name = album_name 
            elif isdir_album_edition == False and edition != None:
                print ("--There is no folder called " + album_name + " (" + str(edition) + ". Rename and move the album.")
                final_album_name = album_name + " (" + str(edition) + ")" 
            elif isdir_album_catalog == False and catalog_number != None:
                print ("--There is no folder called " + album_name + " (Cat# " + str(catalog_number) + ". Rename and move the album.")  
                final_album_name = album_name + " (Cat# " + str(catalog_number) + ")"                 
            elif isdir_album_year == False and original_year != None:
                print ("--There is no folder called " + album_name + " (" + str(original_year) + ". Rename and move the album.")                  
                final_album_name = album_name + " (" + str(original_year) + ")"  
            
            #run windows string cleaning function to remove illegal characters
            #calls the function cleanFilename feeding it the final album name and creating new cleaned variable
            clean_final_album_name = cleanFilename(final_album_name)
              
            #rename album folder
            final_album_path = work_directory + "\\" + clean_final_album_name 
            os.rename(full_work_path,final_album_path)
            print ("--Renamed " + original_folder_name + " to " + clean_final_album_name)    
            
            #move renamed album to artist folder   
            full_artist_folder_path = artist_folder_path + "\\" + clean_final_album_name
            shutil.move(final_album_path, full_artist_folder_path)  
            print ("--Moved " + clean_final_album_name + " to " + artist_name + " directory")   
            
            count +=1 # variable will increment every loop iteration
        #otherwise log that the origin file is missing
        else:
            missing +=1 # variable will increment every loop iteration
            today = datetime.datetime.now()
            #split the director to make sure that it distinguishes between foldrs that should and shouldn't have origin files
            path_segments = directory.split("\\")
            #create different log files depending on whether the origin file is missing somewhere it shouldn't be
            if len(path_segments) == 5:
                #log the missing origin file folders that are likely supposed to be missing
                print ("--Missing origin file logged.")
                the_good_log = log_directory + "\\good-log.txt"
                with open(the_good_log, 'a') as log_file1:
                    log_file1.write("{:%b, %d %Y}".format(today)+ " at " +"{:%H:%M:%S}".format(today)+ ".\n")
                    log_file1.write(directory + "\\ is missing an origin file.\n")
            else:    
                #log the missing origin file folders that are not likely supposed to be missing
                print ("--Missing origin file logged.")
                the_bad_log = log_directory + "\\bad-log.txt"
                with open(the_bad_log, 'a') as log_file2:
                    log_file2.write("{:%b, %d %Y}".format(today)+ " at " +"{:%H:%M:%S}".format(today)+ ".\n")
                    log_file2.write(directory + "\\ is missing an origin file.\n")
        
# Get all the subdirectories of directory_to_check recursively and store them in a list:
directories = [os.path.abspath(x[0]) for x in os.walk(directory_to_check)]
directories.remove(os.path.abspath(directory_to_check)) # If you don't want your main directory included

#  Run a loop that goes into each directory identified in the list and runs the function that caopies and renames the folders
for i in directories:
      os.chdir(i)         # Change working Directory
      sort_rename(i)      # Run your function

#summary text
print("")
print("This script reorganized " + str(count) + " albums. You did the thing!")
print("There were " + str(missing) + " folders with no origin files. Check the log to see what they were.")

# ToDo
# Add error handling album already exists-skip and log
# test in linux
# add some nuance to the windows character replacements