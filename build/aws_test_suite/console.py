import logging


class console:
    @staticmethod
    def log(message=None, level='Info'):
        """
        Prints message to console with the specified level and outputs to log accordingly

        :param message: Message to print
        :type message: str

        :param level: Level of message
        :type level: str
        """

        if message is None:
            pass

        levels = ['Critical', 'Debug', 'Error', 'Info', 'Warning']

        assert level in levels, f'{level} is not a valid level, must be one of Critical, Debug, Error, Info, Warning'

        print(f'({level})~ {message}')

        command = level.lower()
        exec(f'logging.{command}("{message}")')

        if command == 'error':
            print('(Error)~ Exiting.')
            exit(0)

    @staticmethod
    def setup(log_fname="aws-test-suite.log", level="info"):
        """
        Global logger setup

        :param log_fname: Output log filename, defaults to 'aws-test-suite.log'
        :type log_fname: str, optional

        :param level: Output information level, defaults to 'info'
        :type level: str, optional
        """

        # empty out log file
        open(log_fname, 'w').close()
        llevel = {
            "critical": logging.CRITICAL,
            "error": logging.ERROR,
            "warning": logging.WARNING,
            "info": logging.INFO,
            "debug": logging.DEBUG,
            "notset": logging.NOTSET
        }
        log_level = llevel[level]
        logging.basicConfig(format='%(asctime)s: (%(levelname)s)  %(message)s', datefmt='%I:%M:%S %p', level=log_level,
                            handlers=[logging.FileHandler(log_fname), logging.StreamHandler()])
        logging.info(f"AWS Test Suite Logger Initialized\nLog File: {log_fname}\nLog Level: {level}")