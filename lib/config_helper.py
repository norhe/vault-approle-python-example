from ConfigParser import SafeConfigParser
import threading

parser = SafeConfigParser()
use_consul = False


def load_config():
    try:
        global parser
        global use_consul
        parser.read('config.ini')
        use_consul = parser.getboolean('consul', 'use_consul')
        print "we should use Consul: " + str(use_consul)
    except Exception as ex:
        print ex
    finally:
        # reload the config every 15 seconds
        t = threading.Timer(15, load_config)
        t.setDaemon(True)
        t.start()


def get_option(section, option_name):
    if use_consul:
        return _get_option_consul(section, option_name)
    else:
        return _get_option_file(section, option_name)


def _get_option_file(section, option_name):
    try:
        global parser
        return parser.get(section, option_name)
    except Exception as ex:
        print ex


def _get_option_consul(section, option_name):
    return "Not implemented"


load_config()
