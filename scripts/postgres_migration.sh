#!/bin/bash
export PGPASSWORD=postgres  # should not do this in production, use a .pgpass file instead
psql -h localhost -U postgres -d postgres -f ./data/financial_data.sql