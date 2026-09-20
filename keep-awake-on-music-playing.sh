while true; do
    STATE=$(osascript -e '
        tell application "Music"
            if it is running then
                get player state as string
            else
                return "stopped"
            end if
        end tell
    ' 2>/dev/null)

    if [[ "$STATE" == "playing" ]]; then
        caffeinate -i &
        PID=$!

        sleep 30

        kill "$PID" 2>/dev/null
    else
        sleep 30
    fi
done
