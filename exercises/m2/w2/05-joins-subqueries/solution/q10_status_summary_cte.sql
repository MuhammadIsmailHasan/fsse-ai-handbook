WITH per_user AS (
    SELECT user_id,
           COUNT(*) AS total,
           COUNT(*) FILTER (WHERE status IN ('applied', 'interview')) AS active,
           COUNT(*) FILTER (WHERE status = 'offer') AS offers
    FROM applications
    GROUP BY user_id
)
SELECT u.full_name, p.total, p.active, p.offers
FROM per_user p
JOIN users u ON u.id = p.user_id
ORDER BY p.offers DESC, u.full_name;
