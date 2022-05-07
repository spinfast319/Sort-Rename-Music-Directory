# Sort-Rename-Music-Directory
A python script to sort and rename folders based on an origin file for a music library

This project has a dependency on the gazelle-origin project created by x1ppy located here:
https://github.com/x1ppy/gazelle-origin

This script is meant to use yaml origin files to provide standardised metadata to rename music folders. It cycles through folders in a directory loads the yaml origin files inside them and reads what the artist and album name are. It then creates an artist folder and then renames the album to just the album name and moves it into the folder.

It can handle albums with artwork folders or multiple disc folders in them. It can also handle specials characters and removes any characters that makes windows fail. It can also handle multiple versions of the same album. If it finds a folder already exists with the album name it will rename it with additional metadata. It starts with adding the edition if it has one, then it tries the catalog number, then the year. It will fail if versions with those already exists but that could be extended if needed.
