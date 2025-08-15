-- Author: Vinoth
-- Purpose: Top 10 (overall) transactions by amount
SELECT
  state,
  entity_level,
  entity_name,
  SUM(transaction_count)  AS total_transactions,
  SUM(transaction_amount) AS total_amount
FROM top_transaction_data
GROUP BY state, entity_level, entity_name
ORDER BY total_amount DESC
LIMIT 10;
