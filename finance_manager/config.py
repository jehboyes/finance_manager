"""
Module for handling configuration 
"""
from configparser import ConfigParser
import os


class Config(object):
    """
    Configuration object used for variable management

    Uses ConfigParser and local ``config.ini`` to read/write local variables. 
    The ``env`` variable is a bit meta: it holds the name of the section to use when the config 
    is initialised.   
    """

    def __init__(self, verbose=False):
        self.file_name = os.path.join(os.path.dirname(
            os.path.dirname(__file__)), 'config.ini')
        self._cp = ConfigParser()
        self.default_string = "DEFAULT"
        self.env_string = 'env'
        self.verbose = verbose
        if os.path.isfile(self.file_name):
            self._cp.read(self.file_name)
            self.set_section(
                self._cp[self.default_string].get(self.env_string, self.default_string))
        else:
            # First time run locally
            self.set_section(self.default_string)
            defaults = {self.env_string: self.default_string,
                        'database': '',
                        'server': '',
                        'dialect': '',
                        'py_driver': '',
                        'driver': '',
                        'username': '',
                        'password': ''}
            self.write(defaults)

    def set_env(self, name=None):
        name = self.default_string if name is None else name
        self._cp[self.default_string][self.env_string] = name
        self.set_section(name)

    def set_section(self, section):
        """
        Set the name of the environment/section to look for and use
        """
        self.section = section
        self._cp[self.default_string][self.env_string] = section
        if self.section not in self._cp.keys():
            self._cp[self.section] = {}

    def read_section(self, section=None):
        """
        Return all the variables in an environment/section as a formatted string 
        """
        if section is not None:
            self.set_section(section)
        items = [str(item) + "=" + self.read(item)
                 for item in self._cp[self.section]]
        items.sort()
        item_list = "\n".join(items)
        return item_list

    def read(self, item):
        """
        Read a specific item in the current environment/section
        """
        s = self._cp[self.section]
        return s.get(item, "MISSING")

    def write(self, item_dict):
        """
        Update or create config variables in the current environment/section
        """
        for item, value in item_dict.items():
            print(f"{self.section}: Writing {item} as {value}")
            self._cp[self.section][item] = value
        self._save()

    def _save(self):
        with open(self.file_name, "w") as config_file:
            self._cp.write(config_file)
