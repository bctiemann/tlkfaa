#!/bin/sh

case "$1" in
        start)
                sudo -u drawpile drawpile-srv -p 28000 --database /var/drawpile/drawpile.db --sessions /var/drawpile/sessions --templates /usr/local/www/django/tlkfaa/sketcher/templates --web-admin-port 8080 &
                sleep 3
                echo "Started."
                ;;
        stop)
                pkill drawpile-srv
                echo "Stopped."
                ;;
        restart)
                /usr/local/etc/rc.d/drawpile.sh stop
                sleep 5
                /usr/local/etc/rc.d/drawpile.sh start
                echo "Restarted."
                ;;
        *)
                echo ""
                echo "Usage: `basename $0` { start | stop }"
                echo ""
                exit 64
                ;;
esac

