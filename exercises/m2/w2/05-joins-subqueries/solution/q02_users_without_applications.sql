-- Anti-join: LEFT JOIN and keep rows where nothing matched.
SELECT u.full_name
FROM users u
LEFT JOIN applications a ON a.user_id = u.id
WHERE a.id IS NULL;
