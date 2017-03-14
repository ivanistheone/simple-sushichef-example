# Learning Equality backend take home project

Hello! This project should help you get familiar with some parts of Kolibri’s content pipeline.

There are two major components to the content pipeline:

1. The [content workshop](https://contentworkshop.learningequality.org) - A service run by Learning Equality containing all the channels. A channel is a set of content from a content provider, e.g. Khan Academy, that is structured through a tree of topics. Any user can log in and manually create and curate their own channel.
1. The [ricecooker](https://github.com/learningequality/ricecooker/) python package - A framework for programmatically creating a channel on the content workshop. The programmer constructs a tree of nodes pointing to different types of content, and the `ricecooker` automatically fetches and optimizes content before uploading it to the content workshop. This package can be installed by running `pip install ricecooker`.

The `ricecooker` currently requires a programmer to implement a function that returns a tree of nodes.

A balance is needed between an advanced, fully programmatic API; and the ease-of-use of the `content workshop`’s graphical interface. To address this, you’ll need to implement a program that reads a folder tree, and then pass that information along to the `ricecooker` to upload to the `content workshop`.


## Requirements

You are required to submit two deliverables:

1. An python wheel (`.whl`) file, installable through `pip install <yourfile.whl>`.
2. The link to a GitHub repository for your solution that’s able to produce the `.whl` file. **The GitHub repository must have the `MIT` or `BSD` license.**

Your `.whl` file must install a new python executable named `ricecake`. To run the `ricecake`, you’ll need to acquire a `token` on the `content workshop` (see the tutorial linked below). Upon running the `ricecake`  given a folder `folder_path`  with a nested tree of folders with media files (`pdf`, `mp4`, `mp3`) as leaf nodes:

`ricecake --token=<token> <folder_path>`

It must produce a channel on the `content workshop` with the same topic tree structure as the folder given. 

Beside `folder_path` is a `channelmetadata.ini` file. The script should read the `channelmetadata.ini` file to get the attributes for that channel. You are highly encouraged to use the `ricecooker` framework.

Inside the top level folder is a recursive tree of folders, media files, and a `metadata.ini` file. The `metadata.ini` file contains the metadata for the nodes within that tree level. As an example, given a level in the folder tree with the following folders and files:

  Science
  Math
  Philosophy.mp4


Here’s the corresponding `metadata.ini`:

  [Philosophy.mp4]
  title = Philosophy
  license = CC BY
  author = Socrates
  
  [Math]
  title = Math
  description = Learn how to add and subtract!
  
  [Science]
  title = Science
  description = Learn about the wonders of the universe!

Each section corresponds to a node in that folder tree level. Inside each section  are the attributes for that node. You will need to use the attributes within that section when instantiating the `ContentNode` or `TopicNode` that the `ricecooker` reads.

You can acquire a zip file containing sample data [here](https://slack-files.com/T0KT5DC58-F3ZSN3NRL-c50375e9a2).

## Notes
- The `ricecooker` framework is expected to be used in the command line. Given a script `samplechannel.py` that implements a `construct_channel` function:


  `python -m ricecooker uploadchannel samplechannel.py`


  The `ricecooker` will use the tree of `Node`s returned by `samplechannel.construct_channel` to create the channel on the `content workshop`. The easiest way to wrap the `ricecooker` is to use the `subprocess` module to call `ricecooker ` through the shell. Feel free to find a more programmatic way to integrate with the `ricecooker` too.
-  `ContentNode.source_id` ([seen here](https://github.com/jayoshih/ricecooker/tree/readme#step-3-creating-nodes)) needs to be unique within that level. Fortunately the filesystem already enforces uniqueness within a folder level. You can just give the file or folder’s name as the `source_id`.

## What we’re looking for
- We expect the right use of python’s code patterns and standard library, or the use of external libraries which will make your code clearer.
- We are looking for the use of standard python packaging mechanisms and best practices.


## Relevant links (in order of recommended reading)
- [Example folder structure that the ricecake will be run against](https://slack-files.com/T0KT5DC58-F3ZSN3NRL-c50375e9a2)
- [The tutorial for the ricecooker framework](https://github.com/jayoshih/ricecooker/tree/readme)
- [Creating a python package](https://python-packaging.readthedocs.io/en/latest/)
- [Creating an executable script from your package](http://python-packaging.readthedocs.io/en/latest/command-line-scripts.html)
- [The python wheel file format](https://pip.pypa.io/en/stable/reference/pip_wheel/)
- [configparser library (for parsing .ini files)](https://docs.python.org/3/library/configparser.html)
- [The content workshop website](https://contentworkshop.learningequality.org)



