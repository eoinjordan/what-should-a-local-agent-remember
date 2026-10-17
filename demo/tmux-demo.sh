#!/usr/bin/env bash
# The three-terminal layout from the run of show, inside one tmux session:
#   A (top-left)    mongosh agentdemo
#   B (right)       python3 watch.py   (the change-stream consumer)
#   C (bottom-left) idle shell for complete.js / fail.js / propose.js
# Attach locally:  tmux attach -t demo
# Serve to a browser (what the screenshots were taken from):  ttyd -p 7681 -W tmux new -A -s demo
cd "$(dirname "$0")"
tmux kill-session -t demo 2>/dev/null
tmux new-session -d -s demo -x 160 -y 44 -c "$PWD"
tmux split-window -h -t demo -c "$PWD"
tmux split-window -v -t demo:0.0 -c "$PWD"
tmux send-keys -t demo:0.0 'clear; mongosh --quiet agentdemo' C-m
tmux send-keys -t demo:0.2 'clear; python3 watch.py' C-m
tmux select-pane -t demo:0.1
echo "tmux session 'demo' ready: tmux attach -t demo"
