-- Author: Vinoth
-- Purpose: Users & app opens by district within state
SELECT
  state,
  district_state_name,
  SUM(registered_users) AS total_registered_users,
  SUM(app_opens)        AS total_app_opens
FROM map_user_data
GROUP BY state, district_state_name
ORDER BY total_registered_users DESC;
