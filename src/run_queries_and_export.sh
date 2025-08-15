#!/usr/bin/env bash
set -e

HOST="dpg-d2c1kier433s73a8a7p0-a.singapore-postgres.render.com"
USER="phonepe_m8o9_user"
DB="phonepe_data"
PORT="5432"

echo "Running queries..."
psql -h "$HOST" -U "$USER" -d "$DB" -p "$PORT" -f src/sql/queries/aggregated_insurance_by_state.sql
psql -h "$HOST" -U "$USER" -d "$DB" -p "$PORT" -f src/sql/queries/aggregated_transactions_by_state.sql
psql -h "$HOST" -U "$USER" -d "$DB" -p "$PORT" -f src/sql/queries/aggregated_users_by_state_brand.sql
psql -h "$HOST" -U "$USER" -d "$DB" -p "$PORT" -f src/sql/queries/map_insurance_by_district.sql
psql -h "$HOST" -U "$USER" -d "$DB" -p "$PORT" -f src/sql/queries/map_transactions_by_district.sql
psql -h "$HOST" -U "$USER" -d "$DB" -p "$PORT" -f src/sql/queries/map_users_by_district.sql
psql -h "$HOST" -U "$USER" -d "$DB" -p "$PORT" -f src/sql/queries/top_insurance.sql
psql -h "$HOST" -U "$USER" -d "$DB" -p "$PORT" -f src/sql/queries/top_transactions.sql
psql -h "$HOST" -U "$USER" -d "$DB" -p "$PORT" -f src/sql/queries/top_users.sql

echo "Exporting CSVs to docs/outputs/ ..."
psql -h "$HOST" -U "$USER" -d "$DB" -p "$PORT" -c "\COPY ( $(cat src/sql/queries/aggregated_insurance_by_state.sql | sed '/^--/d') ) TO 'docs/outputs/aggregated_insurance_by_state.csv' WITH CSV HEADER"
psql -h "$HOST" -U "$USER" -d "$DB" -p "$PORT" -c "\COPY ( $(cat src/sql/queries/aggregated_transactions_by_state.sql | sed '/^--/d') ) TO 'docs/outputs/aggregated_transactions_by_state.csv' WITH CSV HEADER"
psql -h "$HOST" -U "$USER" -d "$DB" -p "$PORT" -c "\COPY ( $(cat src/sql/queries/aggregated_users_by_state_brand.sql | sed '/^--/d') ) TO 'docs/outputs/aggregated_users_by_state_brand.csv' WITH CSV HEADER"
psql -h "$HOST" -U "$USER" -d "$DB" -p "$PORT" -c "\COPY ( $(cat src/sql/queries/map_insurance_by_district.sql | sed '/^--/d') ) TO 'docs/outputs/map_insurance_by_district.csv' WITH CSV HEADER"
psql -h "$HOST" -U "$USER" -d "$DB" -p "$PORT" -c "\COPY ( $(cat src/sql/queries/map_transactions_by_district.sql | sed '/^--/d') ) TO 'docs/outputs/map_transactions_by_district.csv' WITH CSV HEADER"
psql -h "$HOST" -U "$USER" -d "$DB" -p "$PORT" -c "\COPY ( $(cat src/sql/queries/map_users_by_district.sql | sed '/^--/d') ) TO 'docs/outputs/map_users_by_district.csv' WITH CSV HEADER"
psql -h "$HOST" -U "$USER" -d "$DB" -p "$PORT" -c "\COPY ( $(cat src/sql/queries/top_insurance.sql | sed '/^--/d') ) TO 'docs/outputs/top_insurance.csv' WITH CSV HEADER"
psql -h "$HOST" -U "$USER" -d "$DB" -p "$PORT" -c "\COPY ( $(cat src/sql/queries/top_transactions.sql | sed '/^--/d') ) TO 'docs/outputs/top_transactions.csv' WITH CSV HEADER"
psql -h "$HOST" -U "$USER" -d "$DB" -p "$PORT" -c "\COPY ( $(cat src/sql/queries/top_users.sql | sed '/^--/d') ) TO 'docs/outputs/top_users.csv' WITH CSV HEADER"
echo "Done."
