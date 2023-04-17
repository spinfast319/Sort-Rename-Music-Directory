# Sort-Rename-Music-Directory
### A python script to sort and rename folders based on an origin file for a music library

This script is meant to use yaml origin files to provide standardised metadata to rename music folders. It cycles through folders in a directory loads the yaml origin files inside them and reads what the artist and album name are. It then creates an artist folder and then renames the album to just the album name and moves it into the folder. If the artist already exists, it will just move the album to the right folder.

For example It will take a directory structure like
> Music/[cat#1234]Album Name {year}(flac)  

and transform it into    
> Music/Artist/Album Name  

It can handle albums with artwork folders or multiple disc folders in them. It can also handle specials characters and removes any characters that makes windows fail. It can also handle multiple versions of the same album. If it finds a folder already exists with the album name it will rename it with additional metadata. It starts with adding the edition if it has one, then it tries the catalog number, then the year. It will fail if versions with those already exists but that could be extended if needed. It has been tested and works in both Ubuntu Linux and Windows 10.

This script is meant to work in conjunction with other scripts in order to manage a large music library when the source of the music has good metadata you want to use to organize it.  You can find an overview of the scripts and workflow at [Origin-Music-Management](https://github.com/spinfast319/Origin-Music-Management). 

## Dependencies
This project has a dependency on the gazelle-origin project created by x1ppy. gazelle-origin scrapes gazelle based sites and stores the related music metadata in a yaml file in the music albums folder. For this script to work you need to use a fork that has additional metadata including the tags and coverart. The fork that has the most additional metadata right now is: https://github.com/spinfast319/gazelle-origin

All your albums will need origin files origin files associated with them already for this script to work.

## Install and set up
Clone this script where you want to run it.

Set up or specify the four directories you will be using and specify whether you albums are nested under artist or not.
1. The directory the albums you want to sort and rename are in
2. The directory you want them moved to once you sort and rename them
3. A directory to store the log files the script creates
4. An empty directory the script will use to temporarily hold and rename files before it moves them to the final location
5. Set the album_depth variable to specify whether you are using nested folders or have all albums in one directory
   - If you have all your ablums in one music directory, ie. Music/Album then set this value to 1
   - If you have all your albums nest in a Music/Artist/Album style of pattern set this value to 2

The default is 1 (Music/Album)

Use your terminal to navigate to the directory the script is in and run the script from the command line.  When it finishes it will output how many albums it has moved.

```
Sort-Rename-Music-Directory.py
```

_note: on linux and mac you will likely need to type "python3 Sort-Rename-Music-Directory.py"_  
_note 2: you can run the script from anywhere if you provide the full path to it_

The script will also create logs listing any album that it has problems processing.  
