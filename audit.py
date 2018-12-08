#!/usr/bin/env python2

import os
import shutil
import subprocess

import termcolor

import config


# Directory where the script lives
INSTALL_FOLDER = os.path.dirname(os.path.realpath(__file__))
# Expand evironment variables and metacharacters in the log folder path
config.AUDIT_FOLDER = os.path.expanduser(os.path.expandvars(config.AUDIT_FOLDER))


def log_info(logstr):
    print termcolor.colored('[+] ' + logstr, 'green')


def log_warning(logstr):
    print termcolor.colored('[!] ' + logstr, 'yellow')


def log_error(logstr):
    print termcolor.colored('[X] ' + logstr, 'red')


def get_xdisplay():
    display = subprocess.check_output("who|awk '{print $2}'|sed -n 1p", shell=True).strip()
    if not display.startswith(":"):
        log_warning("Cannot get X display, defaulting to :0")
        display = ":0"
    return display


def get_crontab():
    try:
        crontab = subprocess.check_output(['crontab', '-l'])
    except subprocess.CalledProcessError as e:
        return ""
    return crontab.strip()


def cronjob_exists(command):
    crontab = get_crontab()
    if command in crontab:
        return True
    else:
        return False


def delete_cronjob(command):
    if not cronjob_exists(command):
        log_warning('Trying to remove unexisting cronjob "%s"' % command)
        return
    crontab = get_crontab()
    new_crontab = ""
    for cronjob in crontab.split('\n'):
        if command not in cronjob: 
            new_crontab += cronjob + "\n"
    p1 = subprocess.Popen("crontab", stdin=subprocess.PIPE)
    p1.communicate(new_crontab)


def create_cronjob(command, interval):
    if cronjob_exists(command):
        log_warning('Trying to add already existing cronjob "%s"' % command)
        return
    cronjob = '*/%s * * * * %s' % (interval, command)
    crontab = get_crontab()
    new_crontab = crontab + "\n" + cronjob + "\n"
    p1 = subprocess.Popen("crontab", stdin=subprocess.PIPE)
    p1.communicate(new_crontab)


def get_fullpath(audit_name, create=False):
    fullpath = os.path.join(config.AUDIT_FOLDER, audit_name)
    if not os.path.exists(fullpath):
        if create:
            os.mkdir(fullpath)
        else:
            raise Exception("Audit folder does not exist : %s" % fullpath)
    return fullpath


def get_rcfile():
    if 'zsh' in os.environ['SHELL']:
        rc_file = os.path.join(os.environ['HOME'], '.zshrc')
    else:
        rc_file = os.path.join(os.environ['HOME'], '.bashrc')
    return rc_file


def get_screenshot_command(audit_name):
    return "DISPLAY=" + get_xdisplay() + " " + os.path.join(INSTALL_FOLDER, 'scripts', 'screenshot.py') + " " + os.path.join(get_fullpath(audit_name), 'logs', 'screenshots')


def get_git_command(audit_name):
    return os.path.join(INSTALL_FOLDER, 'scripts', 'git_autocommit.sh') + " " + os.path.join(get_fullpath(audit_name))


def get_source_command(audit_name):
    return 'source ' + os.path.join(get_fullpath(audit_name),'.audit', 'auditrc')


def init(audit_name):
    # Check main directory
    if not os.path.exists(config.AUDIT_FOLDER):
        raise Exception("Main folder %s does not exist." % config.AUDIT_FOLDER)
    
    # Create folder structure
    fullpath = get_fullpath(audit_name, create=True)
    os.makedirs(os.path.join(fullpath, "logs"))
    os.makedirs(os.path.join(fullpath, "logs/screenshots"))
    os.makedirs(os.path.join(fullpath, "logs/shell"))
    os.makedirs(os.path.join(fullpath, ".audit"))
    
    # Create auditrc file
    shutil.copyfile(os.path.join(INSTALL_FOLDER, 'scripts', 'auditrc.sh'), os.path.join(fullpath, '.audit', 'auditrc'))
    
    # Create git repository
    if config.GIT_AUTOCOMMIT:
        subprocess.check_output([os.path.join(INSTALL_FOLDER, 'scripts', 'git_init.sh'), get_fullpath(audit_name)])

    log_info(termcolor.colored('Created audit project in %s' % get_fullpath(audit_name), 'green'))


def start(audit_name):
    # Source auditrc in every shell
    source_command = get_source_command(audit_name)
    with open(get_rcfile(), 'r') as fd1:
        if source_command not in fd1.read():
            with open(get_rcfile(), 'a') as fd2:
                fd2.write('\n' + source_command)
        else:
            log_warning('%s already contains "%s"' % (get_rcfile(), source_command))

    # Create cron jobs
    if config.SCREENSHOTS:
        create_cronjob(get_screenshot_command(audit_name), config.SCREENSHOT_INTERVAL)
    if config.GIT_AUTOCOMMIT:
        create_cronjob(get_git_command(audit_name), config.GIT_AUTOCOMMIT_INTERVAL)
    log_warning('Already opened shells will not be logged')
    os.system('exec ' + os.environ['SHELL'])


def stop(audit_name):
    # Stop auditrc sourcing
    source_command = get_source_command(audit_name)
    new_rc_file = ""
    with open(get_rcfile(), 'r') as fd:
        for line in fd.readlines():
            if line != source_command:
                new_rc_file += line
    with open(get_rcfile(), 'w') as fd:
        fd.write(new_rc_file.strip())

    # Delete cron jobs
    delete_cronjob(get_screenshot_command(audit_name))
    delete_cronjob(get_git_command(audit_name))

    log_info("Audit stopped.")


if __name__ == "__main__":
    from argparse import ArgumentParser
    parser = ArgumentParser(description="audit.py - engagement logging")
    parser.add_argument('action')
    parser.add_argument('audit_name')
    args = parser.parse_args()
    args.audit_name = os.path.basename(args.audit_name)

    if args.action not in ['init', 'start', 'stop']:
        log_error(termcolor.colored('Wrong arguments', 'red'))
        parser.print_help()
        exit(1)

    try:
        if args.action == 'init':
            init(args.audit_name)
        elif args.action == 'start':
            start(args.audit_name)
        elif args.action == 'stop':
            stop(args.audit_name)
    except Exception as exc:
        log_error(str(exc))
