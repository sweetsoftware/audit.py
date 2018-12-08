AUDIT_FOLDER=$(dirname $(dirname $(readlink -f $0)))

if [ "$(ps -ocommand= -p $PPID | awk '{print $1}')" != 'script' ];
    then exec script  -q -f "$AUDIT_FOLDER/logs/shell/$(date +%Y-%m-%d-%H-%M-%S)_shell.log";
fi

echo "\x1b[32mLogging to $AUDIT_FOLDER\x1b[0m"
echo "\x1b[32mStop with : audit.py stop $(basename $AUDIT_FOLDER)\x1b[0m"
