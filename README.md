# AM2DAB
A script for transferring songs from an Apple Music or Spotify playlist to a DAB Music Player Library (https://dab.yeet.su)

# What is needed:

- DAB Music Player account
- Apple Music or Spotify playlist exported in CSV format ([playlists.cloud](playlists.cloud) recommended)
- Python 3.x (tested with 3.13.7)
- Requests

# Compatibility List:

- [https://dab.yeet.su](https://dab.yeet.su)

*May work on other DAB Music Player sites, but would need modifications.*

# How to Use:

- Download or git clone the repository... or just download AM2DAB.py and place it in an empty folder.
- Place exported CSV of Apple Music or Spotify Playlist in the directory, and rename it to music.csv
- Run the python script in a terminal, no additional args needed.
- Wait patiently for most, if not all of your music to be added to a newly created library on DAB Music Player.

# Important Information About Using Exported CSV From Other Sources (Untested, Not Recommended):

In theory, it should be possible to use an exported CSV from other sources, but here are what spreadsheet rows are required in the CSV for this to work:

- artist - Artists of the songs you're adding.
- track_name - Name of the songs you're adding.
- album_name - Name of the albums the songs you're adding are from. 
- isrc - ISRC of the particular songs you're adding.

We've included an example CSV on how it can look.

# Possible Future Features:

- Choice for custom library name and description.
- Add songs to existing library. Skip existing songs in existing library.
- Provide a document containing all songs that failed.
- Manual song search/add for songs that failed.
- Exporting playlists via the script before transfer.
