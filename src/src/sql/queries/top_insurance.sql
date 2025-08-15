-- Author: Vinoth
-- Purpose: Top 10 (overall) insurance by premium
SELECT
  state,
  entityname,
  type,
  SUM(count)  AS total_policies,
  SUM(amount) AS total_amount
FROM top_insurance_data
GROUP BY state, entityname, type
ORDER BY total_amount DESC
LIMIT 10;
