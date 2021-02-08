class bcolors:
    NOTICE = '\033[7m'
    SUCCESS = '\033[92m'
    WARNING = '\033[93m'
    ERROR = '\033[91m'
    FATAL = '\033[45m'
    ENDC = '\033[0m'


def log_notice(str_: str):
    print(f"-N {str_}")


def log_success(str_: str):
    print(f"{bcolors.SUCCESS}-S {str_}{bcolors.ENDC}")


def log_warning(str_: str):
    print(f"{bcolors.WARNING}-W {str_}{bcolors.ENDC}")


def log_error(str_: str):
    print(f"{bcolors.ERROR}-E {str_}{bcolors.ENDC}")


def log_fatal(str_: str):
    print(f"{bcolors.FATAL}-F {str_}{bcolors.ENDC}")