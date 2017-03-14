# simple-sushichef-example
Simple sushichef script that uploads media files to the content curation workshop


Install
-------
Clone this project to your computer then follow these steps:

1. Create a virtual environment

    virtualenv -p python3.5 .cake

2. Activate the virtualenv

    source .cake/bin/activate
    
3. Install the `ricecooker` python package

    pip install ricecooker


Download media files
--------------------
The script `getsampledata.sh` will download a 80MB zip file with the media files
that we'll use for this test. Run the following command from the command line:

    ./getsampledata.sh

Does this work on Windows?



Run
---
Create an account at [content workshop](https://contentworkshop.learningequality.org)
and obtain your token (in Profile --> Settings).

Assuming you followed the above steps, you can now run

    ./ricecake.py  sampledata/my\ first\ ricecooker  --token=70aec00000000000000000000000000000000ed4

where you have to replace `78aec...` with your token.




TODO
----

Finish packaging & generating standalone installable wheel 
  - https://packaging.python.org/distributing/
  - https://github.com/pypa/sampleproject
  - https://www.blog.pythonlibrary.org/2014/01/10/python-packaging-wheel/

Test wheel works on Windows




