from bioblend.galaxy import GalaxyInstance
import argparse
import os
import logging
import time

def get_args():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-a', '--api-key',
                            required=True,
                            help='Admin API Key')
    arg_parser.add_argument('-u', '--url',
                            required=True,
                            help='Galaxy URL')
    arg_parser.add_argument('--debug',
                            action='store_true',
                            default=False,
                            help='Print debug information')
    args = arg_parser.parse_args()
    return args

def set_logging_level(debug=False):
    logging.basicConfig(
        level=logging.DEBUG if debug else logging.INFO,
        format='%(asctime)s - %(message)s',
        datefmt='%d-%m-%y %H:%M:%S')

def main():
    """
    Downloads singularity containers on a Galaxy instance which is configured
    to use such dependency resolvers (mulles_singularity and cached_mulled_singularity).

    It will request the resolution of tools to containers from the instance,
    and then for all mulled_singularity resolved tools that are pointing to
    docker://<container-url>, it will download and build the singularity SIF.
    This download is done only once per container, and applies after for all tools
    that will make use of it.
    """
    args = get_args()
    set_logging_level(debug=args.debug)
    gi = GalaxyInstance(url=args.url, key=arg.key)

    tools_deps = gi.make_get_request(gi.base_url + "/api/container_resolvers/toolbox").json()

    # We keep a container url to tools, since the
    # RAW API call to download a container requires a tool identifier (but only one).
    container2tool_id = dict()
    for tool_deps in tools_deps:
        if 'container_description' in tool_deps['status']:
            if 'identifier' in tool_deps['status']['container_description']:
                if tool_deps['status']['container_description']['identifier'].startswith("docker://"):
                    container2tool_id[tool_deps['status']['container_description']['identifier']] = tool_deps['tool_id']

    downloads = 0
    for cont in container2tool_id:
        logging.info(f"Retrieving container {cont}...")
        tool_id = container2tool_id[cont]
        try:
            result = gi.make_post_request(url=gi.base_url + "/api/container_resolvers/toolbox/install",
                                          payload={ "tool_ids": [tool_id]})
        except ConnectionError as e:
            logging.warning("Connection interrupted... waiting for potential download before proceeding with next container.")
            time.sleep(20)
        downloads += 1


    logging.info(f"Downloaded {downloads} containers.")


if __name__ == '__main__':
    main()
