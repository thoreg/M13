#!/bin/bash
DATE=`date +%Y%m%dT%H%M`
pg_dump m13 > dumps/${DATE}-m13.sql
