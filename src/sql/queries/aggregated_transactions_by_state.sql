-- Author: Vinoth
-- Purpose: Transactions totals by state
SELECT
  state,
  SUM(transaction_count)  AS total_transactions,
  SUM(transaction_amount) AS total_amount
FROM aggregated_transaction_data
GROUP BY state
ORDER BY total_transactions DESC;
