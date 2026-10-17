#!/usr/bin/env bash
# Non-interactive end-to-end run of every demo step. Used to validate the kit;
# exits non-zero if any step's expected line is missing.
set -u; cd "$(dirname "$0")"
PASS=0; FAIL=0
step(){ printf '\n\033[1;36m== %s ==\033[0m\n' "$*"; }
check(){ if grep -q "$2" "$1"; then echo "  [PASS] $3"; PASS=$((PASS+1)); else echo "  [FAIL] $3"; FAIL=$((FAIL+1)); fi; }

step "reset";     mongosh --quiet reset.js | tee /tmp/d-reset.log
check /tmp/d-reset.log "run-1842 is training" "run-1842 back on training"

step "slide 10";  mongosh --quiet demo1-findone.js | tee /tmp/d-10.log
check /tmp/d-10.log "run-1842" "findOne returns the slide-10 document"

step "slide 12";  mongosh --quiet demo-index.js | tee /tmp/d-12.log
check /tmp/d-12.log "projectId_1_status_1" "Q1 uses {projectId, status}"
check /tmp/d-12.log "projectId_1_updatedAt_-1" "Q2 uses {projectId, updatedAt:-1}"

step "slide 14 watcher (background)"; python3 watch.py > /tmp/d-watch.log 2>&1 & WP=$!; sleep 2
step "slide 14 complete.js"; mongosh --quiet complete.js; sleep 2; cat /tmp/d-watch.log
check /tmp/d-watch.log "agent.resume(thread_id='run-1842')" "watcher fired on completed"

step "slide 14 resume path: kill watcher, fail the run while it is down, restart"; kill $WP; sleep 1
mongosh --quiet fail.js; python3 watch.py > /tmp/d-watch2.log 2>&1 & WP=$!; sleep 3; cat /tmp/d-watch2.log; kill $WP
check /tmp/d-watch2.log "resuming after saved token" "restart used the saved resume token"
check /tmp/d-watch2.log "status=.*failed" "event sent while down was delivered after restart"

step "slide 15";  mongosh --quiet ttl.js | tee /tmp/d-15.log
check /tmp/d-15.log "sessions now: 2" "two sessions written with per-document expiresAt"

step "slide 17";  mongosh --quiet queries.js | tee /tmp/d-17.log
check /tmp/d-17.log "failureEmbedding" "structured query returns the failed run with its embedding beside it"

step "slide 18 governor (background)"; python3 governor.py > /tmp/d-gov.log 2>&1 & GP=$!; sleep 2
step "slide 18 propose.js"; mongosh --quiet propose.js | tee /tmp/d-18.log; cat /tmp/d-gov.log; kill $GP
check /tmp/d-gov.log "APPROVED.*start_training" "start_training approved by policy"
check /tmp/d-gov.log "REJECTED.*deploy_model" "deploy_model rejected: no policy"
check /tmp/d-18.log "REFUSED.*delete_project" "delete_project refused by schema at insert"

step "slide 15 again, after the TTL monitor has run (it sweeps about once a minute; waiting up to 150 s)"
for i in $(seq 1 30); do [ "$(mongosh --quiet agentdemo --eval 'db.sessions.countDocuments()')" = "1" ] && break; sleep 5; done
mongosh --quiet ttl-check.js | tee /tmp/d-15b.log
check /tmp/d-15b.log "sessions now: 1" "sess-1842 expired, sess-1841 kept"

printf '\n%d passed, %d failed\n' "$PASS" "$FAIL"; [ "$FAIL" -eq 0 ]
