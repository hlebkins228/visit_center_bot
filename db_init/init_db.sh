#!/bin/bash

sudo -u postgres psql -f DBcreate.sql
sudo -u postgres psql -d visit_center -f DBsetup.sql
sudo -u postgres psql -d visit_center -f DBconstrains.sql
sudo -u postgres psql -d visit_center -f DBcreateBotUser.sql