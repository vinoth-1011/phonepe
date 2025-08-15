-- Author: Vinoth
-- Purpose: Transaction totals by district within state
SELECT
  state,
  district_state_name,
  SUM(transaction_count)  AS total_transactions,
  SUM(transaction_amount) AS total_amount
FROM map_transaction_data
GROUP BY state, district_state_name
ORDER BY total_transactions DESC;
