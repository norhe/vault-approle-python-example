from ConfigParser import SafeConfigParser

# assumes config.ini is in the same directory as config_helper.py
def get_option(section, option_name):
    parser = SafeConfigParser()
    parser.read('config.ini')
    print parser.sections()
    try:
        print section + str(parser.options(section))
        return parser.get(section, option_name)
    except Exception as ex:
        #print ex.message
        print ex
