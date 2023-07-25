"""dynvertest package

Test dynamic versioning in a Python package.
"""


import argparse
from importlib import metadata
import time

fallback_version = "0.0.1"


def epochversion():
    """Return a verison number based on the epoch"""
    epoch = int(time.time())
    return "0.0.{}".format(epoch)


def main():
    parser = argparse.ArgumentParser(description="Dynamic version testing")
    args = parser.parse_args()
    print(f"Package version (generated in code and set at package installation time):   {metadata.version(__name__)}")
    print(f"New dynamic version (generated at program runtime):                         {epochversion()}")
    print(f"Fallback version (defined statically in the Python code):                   {fallback_version}")
