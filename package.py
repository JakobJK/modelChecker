name = "modelChecker"


@early()
def version():
    import sys, os

    sys.path.append(os.getcwd())

    import modelChecker

    return modelChecker.__version__


help = "https://jakejk.io/modelChecker"

description = " Sanity checking tool for polygon models in Maya"

authors = ["Jakob Kousholt", "Niels Peter Kaagaard "]

variants = [["python-2.7"], ["python-3+<4"]]


def commands():
    env.PYTHONPATH.append("{root}/python")
