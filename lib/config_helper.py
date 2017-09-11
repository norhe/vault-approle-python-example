from ConfigParser import SafeConfigParser

def get_option(option_name):
    parser = SafeConfigParser()
    parser.read('../config.ini')
    return parser.get(option_name)
