-- Author: Vinoth
-- Date: 2025-08-15
-- Purpose: Show total registered users by state
SELECT state,
       SUM(registered_users) AS total_registered_users,
       SUM(app_open_count)   AS total_app_opens
FROM aggregated_user_data
GROUP BY state
ORDER BY total_registered_users DESC;
