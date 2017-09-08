#!/usr/bin/env python

import argparse
import configparser
import os
import sys

from ricecooker.chefs import SushiChef
from ricecooker.classes import nodes, files
from le_utils.constants import content_kinds
from ricecooker.commands import uploadchannel


IGNORABLE_FILENAMES = ['.DS_Store']



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
    # print('path_as_list=', path_as_list)
    current = channel
    for subtopic in path_as_list:
        current = list(filter(lambda d: d.title == subtopic, current.children))[0]
    return current



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
        if filename in IGNORABLE_FILENAMES:
            continue
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




# CHEF
################################################################################

class RicecakeSushiChef(SushiChef):
    """
    Sushi chef that reads the files from a given directory structure and turns
    them into a Kolibri channel.
    """

    def __init__(self, *args, **kwargs):
        super(RicecakeSushiChef, self).__init__(*args, **kwargs)
        self.arg_parser = argparse.ArgumentParser(
            description="Upload a folder hierarchy to the content workshop.",
            parents=[self.arg_parser]
        )
        self.arg_parser.add_argument('--folder_path', help='A folder with files to upload')


    def get_channel(self, **kwargs):
        # read channelmetadata.ini
        channel_files_folder = os.path.abspath(kwargs['folder_path'])
        channel_ini_filepath = os.path.join(channel_files_folder, '..', 'channelmetadata.ini')
        channel_config = configparser.ConfigParser()
        channel_config.read(channel_ini_filepath)

        # create channel
        channel = nodes.ChannelNode(
            source_domain = channel_config.get('channeldata', 'domain'),
            source_id = channel_config.get('channeldata', 'source_id'),
            title = channel_config.get('channeldata', 'title'),
            thumbnail = "https://upload.wikimedia.org/wikipedia/commons/thumb/3/33/Quaker-Popped-Rice-Snacks.jpg/320px-Quaker-Popped-Rice-Snacks.jpg",
            language = 'en',
        )
        return channel


    def construct_channel(self, **kwargs):
        """
        Create a channel from filesytem tree staring at `folder_path`.
        Needs to have channelmetata.ini in the same folder as `folder_path`.

        Uses `process_folder` for the actual work.
        """
        channel = self.get_channel(**kwargs)

        channel_files_folder = os.path.abspath(kwargs['folder_path'])
        (parent, folder_path) = os.path.split(channel_files_folder)
        # print('parent=', parent)
        # print('folder_path=', folder_path)
        os.chdir(channel_files_folder)
        os.chdir('..')
        # print('cwd=', os.getcwd())
        content_folders = list(os.walk(folder_path))
        # print(content_folders)

        print('processing channel...')
        # Skip over channel folder because handled above
        _ = content_folders.pop(0)
        # handle each subfolder
        for raw_path, subfolders, filenames in content_folders:
            print('processing a subfloder')
            process_folder(channel, raw_path, subfolders, filenames)

        return channel



# CLI
################################################################################

if __name__ == '__main__':
    ricecake_chef = RicecakeSushiChef()
    ricecake_chef.main()

