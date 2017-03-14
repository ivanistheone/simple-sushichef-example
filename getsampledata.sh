#!/usr/bin/env bash
# Downloads the backendtest.zip file to a subdirectory in current directory
MEDIADIR='sampledata'

if [ ! -d $MEDIADIR ]; then 
  mkdir $MEDIADIR
fi
cd $MEDIADIR 

echo "Downloading sample media files to $MEDIADIR"
wget "https://files.slack.com/files-pri/T0KT5DC58-F3ZSN3NRL/download/backendtest.zip?pub_secret=c50375e9a2" -O backendtest.zip
unzip backendtest.zip
rm backendtest.zip


