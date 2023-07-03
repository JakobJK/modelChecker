from setuptools import setup, find_packages


def get_version():
    with open("modelChecker/__version__.py", "r") as f:
        for line in f:
            if line.startswith("__version__"):
                return line.split("=")[-1].strip().strip('"')
    raise ValueError("Could not find version string.")


setup(
    name="modelChecker",
    version=get_version(),
    description="Sanity checking tool for polygon models in Maya",
    author="Jakob Kousholt, Niels Peter Kaagaard",
    packages=find_packages(),
)
