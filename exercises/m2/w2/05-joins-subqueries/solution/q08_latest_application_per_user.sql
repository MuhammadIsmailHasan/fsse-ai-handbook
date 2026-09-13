-- Window function: number each user's applications from newest, keep number 1.
WITH ranked AS (
    SELECT a.user_id, a.role_title, a.applied_on,
           ROW_NUMBER() OVER (PARTITION BY a.user_id ORDER BY a.applied_on DESC, a.id DESC) AS rn
    FROM applications a
)
SELECT u.full_name, r.role_title, r.applied_on
FROM ranked r
JOIN users u ON u.id = r.user_id
WHERE r.rn = 1
ORDER BY u.full_name;
