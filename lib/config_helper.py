from ConfigParser import SafeConfigParser

def get_option(section, option_name):
    parser = SafeConfigParser()
    parser.read('../config.ini')
    print parser.sections()
    return parser.get(section, option_name)
