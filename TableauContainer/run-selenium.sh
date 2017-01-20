#!/bin/bash
Xvfb $DISPLAY &
pid=$!
sleep 5
webdriver-manager start --detach
sleep 10
$1
webdriver-manager shutdown
kill -9 $pid
