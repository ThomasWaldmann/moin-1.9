# -*- coding: iso-8859-1 -*-
"""
    MoinMoin - init "logging" system

    WARNING
    -------
    logging must be configured VERY early, before any moin module calls
    log.getLogger(). Because most modules call getLogger on the module
    level, this basically means that MoinMoin.log must be imported first
    and load_config must be called afterwards, before any other moin
    module gets imported.

    Usage
    -----
    Typically, do this at top of your module:

    from MoinMoin import log
    logging = log.getLogger(__name__)

    This will create a logger with 'MoinMoin.your.module' as name.
    The logger can optionally get configured in the logging configuration.
    If you don't configure it, some upperlevel logger (e.g. the root logger)
    will do the logging.

    @copyright: 2008 MoinMoin:ThomasWaldmann
    @license: GNU GPL, see COPYING for details.
"""

# This is the "last resort" fallback logging configuration for the case
# that load_config() is either not called at all or with a non-working
# logging configuration.
# See http://www.python.org/doc/lib/logging-config-fileformat.html
# We just use moin.log in current directory by default, if you want
# anything else, override logging_conf in your server script's Config class.
logging_defaults = {
    'logdir': '.',
    'loglevel': 'DEBUG',
}
logging_config = """\
[loggers]
keys=root

[handlers]
keys=logfile,stderr

[formatters]
keys=logfile

[logger_root]
level=%(loglevel)s
handlers=logfile,stderr

[handler_logfile]
class=FileHandler
level=NOTSET
formatter=logfile
args=('%(logdir)s/moin.log', 'at')

[handler_stderr]
class=StreamHandler
level=NOTSET
formatter=logfile
args=(sys.stderr, )

[formatter_logfile]
format=%(asctime)s %(levelname)s %(name)s:%(lineno)d %(message)s
datefmt=
class=logging.Formatter
"""

from MoinMoin.support import logging_fix
import logging, logging.config

configured = False
fallback_config = False

strip_MoinMoin = False

def load_config(conf_fname):
    """ load logging config from conffile """
    global configured
    try:
        logging.config.fileConfig(conf_fname)
        configured = True
    except Exception, err: # XXX be more precise
        load_fallback_config(err)

def load_fallback_config(err=None):
    """ load builtin fallback logging config """
    global configured
    from StringIO import StringIO
    logging.config.fileConfig(StringIO(logging_config), logging_defaults)
    configured = True
    l = getLogger(__name__)
    l.warning('Using built-in fallback logging configuration!')
    if err:
        l.warning('load_config failed with "%s".' % str(err))


def getLogger(name):
    """ wrapper around logging.getLogger, so we can do some more stuff:
        - preprocess logger name
        - patch loglevel constants into logger object, so it can be used
          instead of the logging module
    """
    global configured
    if not configured: # should not happen
        load_fallback_config()
    if strip_MoinMoin and name.startswith('MoinMoin.'):
        name = name[9:]
    logger = logging.getLogger(name)
    for levelnumber, levelname in logging._levelNames.items():
        if isinstance(levelnumber, int): # that list has also the reverse mapping...
            setattr(logger, levelname, levelnumber)
    return logger

