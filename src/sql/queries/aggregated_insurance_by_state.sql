-- Author: Vinoth
-- Purpose: Insurance totals by state
SELECT
  state,
  SUM(transaction_count)  AS total_policies,
  SUM(transaction_amount) AS total_amount
FROM aggregated_insurance_data
GROUP BY state
ORDER BY total_policies DESC;
