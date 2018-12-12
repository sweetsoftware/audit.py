
if [ -n "$ZSH_VERSION" ]; then
    AUDIT_FOLDER=$(dirname $(dirname $(readlink -f $0)))
    AUDIT_NAME=$(basename $AUDIT_FOLDER)
    PROMPT='%{$fg_bold[green]%}%n@%m%{$reset_color%}:%{$fg_bold[blue]%}%~ %{$fg_bold[red]%}[IP: `ip route get 1 2>/dev/null|sed -n 1p|rev|cut -f2 -d" "|rev`]%{$fg_bold[white]%} %W-%*%{$reset_color%}
$ '

elif [ -n "$BASH_VERSION" ]; then
	AUDIT_FOLDER=$(dirname $(dirname $BASH_SOURCE))
	AUDIT_NAME=$(basename $AUDIT_FOLDER)
	PS1='\033[32;1m\u@\h\033[0m:\033[34;1m\W\033[0m [IP: \033[0;1m`ip route get 1 2>/dev/null|sed -n 1p|rev|cut -f2 -d" "|rev`]\033[0m `date +"%D-%T"`\n$ '
fi

if [ "$(ps -ocommand= -p $PPID | awk '{print $1}')" != 'script' ];
then
    export LOGFILE="$AUDIT_FOLDER/logs/shell/$(date +%Y-%m-%d-%H-%M-%S)_shell.log"
    exec script -q -f "$AUDIT_FOLDER/logs/shell/$(date +%Y-%m-%d-%H-%M-%S)_shell.log";
fi

echo -e "\x1b[32mLogging to $LOGFILE"
echo -e "Stop with : audit.py stop $AUDIT_NAME\x1b[0m"
