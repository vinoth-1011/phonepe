-- Author: Vinoth
-- Purpose: Insurance totals by district within state
SELECT
  state,
  district_state_name,
  SUM(count)  AS total_policies,
  SUM(amount) AS total_amount
FROM map_insurance_data
GROUP BY state, district_state_name
ORDER BY total_policies DESC;
