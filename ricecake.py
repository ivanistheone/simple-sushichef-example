#!/usr/bin/env python

import argparse
import configparser
import os
import sys

from ricecooker.classes import nodes, files
from le_utils.constants import content_kinds
from ricecooker.commands import uploadchannel


# HELPER METHODS
################################################################################
def get_path_as_list(path):
    """
    Convert raw_path form os.walk tuple format to a list of subdirectories.
    The list of paths is returned without top-level channel directory.
    """
    full_path = path.split(os.path.sep)
    path_without_channel = full_path[1:]
    return path_without_channel

def get_node_for_path(channel, path_as_list):
    """
    Returns the TopicNode at the given path.
    """    
    current = channel
    for subtopic in path_as_list:
        current = list(filter(lambda d: d.title == subtopic, current.children))[0]
    return current



# CHANNEL MAIN
################################################################################
def construct_channel(**kwargs):
    """
    Create a channel from filesytem tree staring at `folder_path`.
    Needs to have channelmetata.ini in the same folder as `folder_path`.
    
    Uses `process_folder` for the actual work.
    """
    folder_path = kwargs['folder_path']
    content_folders = list(os.walk(folder_path))
    
    # global data structure channel
    channel = {}
    
    print('processing channel...')

    # read channelmetadata.ini
    parent_path, _ = os.path.split(folder_path)
    channel_ini_filepath = os.path.join(parent_path, 'channelmetadata.ini')
    channel_config = configparser.ConfigParser()
    channel_config.read(channel_ini_filepath)

    # create channel
    channel = nodes.ChannelNode(
        source_domain = channel_config.get('channeldata', 'domain'),
        source_id = channel_config.get('channeldata', 'source_id'),
        title = channel_config.get('channeldata', 'title'),
        thumbnail = "https://upload.wikimedia.org/wikipedia/commons/thumb/3/33/Quaker-Popped-Rice-Snacks.jpg/320px-Quaker-Popped-Rice-Snacks.jpg",
    )
    
    # Skip over channel folder because handled above
    _ = content_folders.pop(0)
    # handle each subfolder
    for raw_path, subfolders, filenames in content_folders:
        print('processing a subfloder')
        process_folder(channel, raw_path, subfolders, filenames)

    return channel


# FOLDER PROCESSING
################################################################################
def process_folder(channel, raw_path, subfolders, filenames):
    """
    Create `ContentNode`s from each file in this folder and the node to `channel`
    under the path `raw_path`.
    """
    path_as_list = get_path_as_list(raw_path)
    
    # A. TOPIC
    topic_title = path_as_list.pop()
    parent_node = get_node_for_path(channel, path_as_list)

    # read parent metadata to get title and description
    parent_path, _ = os.path.split(raw_path)
    ini_filepath = os.path.join(parent_path, 'metadata.ini')
    parent_config = configparser.ConfigParser()
    parent_config.read(ini_filepath)

    # create topic
    topic = nodes.TopicNode(
        source_id=raw_path,
        title=parent_config.get(topic_title, 'title'),
        description=parent_config.get(topic_title, 'description', fallback=None),
    )
    parent_node.add_child(topic)

    # remove metadata.ini from filenames list
    assert 'metadata.ini' in filenames
    filenames.remove('metadata.ini')

    # B. PROCESS FILES
    files_config = configparser.ConfigParser()
    folder_ini = os.path.join(raw_path, 'metadata.ini')
    files_config.read(folder_ini)
    for filename in filenames:
        file_key, file_ext = os.path.splitext(filename)
        ext = file_ext[1:]
        kind = None
        if ext in content_kinds.MAPPING:
            kind = content_kinds.MAPPING[ext]
        # prepare node data
        filepath = os.path.abspath(os.path.join(raw_path, filename))
        source_id = os.path.join(raw_path, filename)
        license = files_config.get(file_key, 'license')
        title = files_config.get(file_key, 'title')
        optionals = {}
        optionals['author'] = files_config.get(file_key, 'author', fallback=None)
        optionals['description'] = files_config.get(file_key, 'description', fallback=None)
        node = make_content_node(kind, source_id, title, license, filepath, optionals)
        # attach to containing topic
        topic.add_child(node)


def make_content_node(kind, source_id, title, license, filepath, optionals):
    """
    Create `kind` subclass of ContentNode based on required args and optionals.
    """
    content_node = None
    if kind == content_kinds.VIDEO:
        content_node = nodes.VideoNode(
            source_id=source_id,
            title=title,
            license=license,
            author=optionals.get("author", None),
            description=optionals.get("description", None),
            derive_thumbnail=True, # video-specific data
            files=[files.VideoFile(path=filepath)],
        )

    elif kind == content_kinds.AUDIO:
        content_node = nodes.AudioNode(
            source_id=source_id,
            title=title,
            license=license,
            author=optionals.get("author", None),
            description=optionals.get("description", None),
            thumbnail=optionals.get("thumbnail", None),
            files=[files.AudioFile(path=filepath)],
        )
    
    elif kind == content_kinds.DOCUMENT:
        content_node = nodes.DocumentNode(
            source_id=source_id,
            title=title,
            license=license,
            author=optionals.get("author", None),
            description=optionals.get("description", None),
            thumbnail=optionals.get("thumbnail", None),
            files=[files.DocumentFile(path=filepath)],
        )
    
    return content_node


def main():
    parser = argparse.ArgumentParser(description="Upload a folder hierarchy to the content workshop.")
    parser.add_argument('--token', required=True, help='Token from content workshop')
    parser.add_argument('folder_path', help='A folder with files to upload')
    args = parser.parse_args()
    input_path = args.folder_path
    token = args.token
    
    # save current module name before chdir
    this_module = os.path.abspath(__file__)
    
    # change path to be in parent dir of `folder_path`
    os.chdir(input_path)
    os.chdir('..')
    
    # get name for channel folder
    input_path = input_path.rstrip(os.path.sep)
    (parent, folder_path) = os.path.split(input_path)
    # construct_channel(folder_path=folder_path)
    
    uploadchannel(this_module, folder_path=folder_path, token=token, verbose=True, reset=True)


if __name__ == '__main__':
    main()
