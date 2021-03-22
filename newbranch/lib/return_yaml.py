import sys
import yaml

def read_settings(file):
    try:
        F = open(file, 'r')
        configSettings = yaml.load(F.read(), Loader=yaml.FullLoader)
    except FileNotFoundError:
        print("File: settings.yaml not found. Can not continure.")
        sys.exit(1)
    except Exception as e:
        print("Caught unknown error trying to read settings.yaml. Can not continue.")
        print("Check yaml syntax.")
        print(e)
        sys.exit(1)
    return configSettings
