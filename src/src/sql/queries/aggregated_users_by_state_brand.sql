-- Author: Vinoth
-- Purpose: App transactions & share by state + brand
SELECT
  state,
  brand,
  SUM(transaction_count)           AS total_transactions,
  AVG(transaction_percentage)      AS avg_transaction_percentage
FROM aggregated_user_data
GROUP BY state, brand
ORDER BY total_transactions DESC;
