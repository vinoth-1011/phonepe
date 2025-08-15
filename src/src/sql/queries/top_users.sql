-- Author: Vinoth
-- Purpose: Top 10 districts by registered users
SELECT
  state,
  district,
  SUM(registeredusers) AS total_registered_users
FROM top_user_data
GROUP BY state, district
ORDER BY total_registered_users DESC
LIMIT 10;
