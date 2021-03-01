import logging
from datetime import datetime
import sys
import os
import glob


def trim_logs(logger, max_logs, log_dir):

    logger.info("Trimming logs to " + str(max_logs) + " logs.")
    try:
        os.chdir(log_dir)
    except OSError:
        logger.critical("Can not chdir to " + log_dir + " Exiting.")
        sys.exit(1)

    file_list = []
    for file in glob.glob("*.log"):
        try:
            pre, dt, ext = file.split('.')
            file_list.append({ 'dt': datetime.strptime(dt, '%Y-%m-%d-%H-%M-%S'), 'file': file })
        except:
            logger.critical("I don't know how to extract the date time from " + file + " file.")
            sys.exit(1)

    ordered = sorted(file_list, key=lambda i: (i['dt']), reverse=True)
    while(len(ordered) > max_logs):

        file = ordered.pop()
        try:
            os.unlink(file['file'])
            logger.info("Removed " + file['file'] + " file.")
        except:
            logger.critical("Can not delete " + file['file'] + " file.")
            sys.exit(1)


def setup_logging(log_dir,console_error_level, file_error_level):

    if not os.path.isdir(log_dir):
        try:
            os.makedirs(log_dir)
        except OSError:
            print(now() + "No directory: " + log_dir +
                  " found.  Could not create it. Exiting")
            sys.exit(1)
        else:
            print(now() + "Unknown error attempting to create " + log_dir + " directory.")
            sys.exit(1)
    try:
        os.chdir(log_dir)
    except OSError:
        print(now() + "Can not chdir to " + log_dir + " to set up logging.")
        sys.exit(1)
    logtime = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    logfile = "array_annual." + logtime + '.log'

    file_error_level = eval("logging." + file_error_level)
    console_error_level = eval("logging." + console_error_level)
    logger = logging.getLogger('array_annual')
    logger.setLevel(file_error_level)
    fh = logging.FileHandler(logfile)
    ch = logging.StreamHandler()
    ch.setLevel(console_error_level)
    fh.setLevel(file_error_level)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s ==> %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    logger.addHandler(fh)
    logger.addHandler(ch)

    return logger
