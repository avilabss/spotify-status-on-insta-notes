import os

from configparser import ConfigParser


settings_file = os.path.join(os.getcwd(), "session_metadata.json")
config_file = os.path.join(os.getcwd(), "config.ini")

config = ConfigParser()
config.read(config_file)