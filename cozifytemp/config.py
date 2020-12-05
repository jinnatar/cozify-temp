import configparser
import os

def _initXDG(program_name):
    # per the XDG basedir-spec we adhere to $XDG_CONFIG_HOME if it's set, otherwise assume $HOME/.config
    xdg_config_home = ''
    if 'XDG_CONFIG_HOME' in os.environ:
        xdg_config_home = os.environ['XDG_CONFIG_HOME']
    else:
        xdg_config_home = "%s/.config" % os.path.expanduser('~')

    # XDG base-dir: "If, when attempting to write a file, the destination directory is non-existant an attempt should be made to create it with permission 0700. If the destination directory exists already the permissions should not be changed."
    if not os.path.isdir(xdg_config_home):
        os.mkdir(xdg_config_home, 0o0700)

    # finally create our own config dir
    config_dir = "%s/%s" % (xdg_config_home, program_name)
    if not os.path.isdir(config_dir):
        os.mkdir(config_dir, 0o0700)

    return config_dir + '/'

def _initState(config_file):
    # set defaults, these are used if the config doesn't override
    config = configparser.ConfigParser()
    config.read_dict({'Storage':
        {
            'url': 'http://localhost:8086',
            'token': '',
            'organization': '',
            'bucket': 'cozify'
        }
    })

    try:
        cf = open(config_file, 'r')
    except IOError: # if open fails, let's try to write one
        cf = open(config_file, 'w+') # if this fails, let it burn
        os.chmod(config_file, 0o600)
        # now we should have a blank config_file so let's write out the defaults
        config.write(cf)
    else: # file is readable so let's read it in and override defaults
        config.read_file(cf)

    return config

config_file = _initXDG('cozify-temp') + 'influxdb.cfg'
config = _initState(config_file)
