SELECT u.full_name
FROM users u
WHERE EXISTS (
    SELECT 1 FROM applications a
    WHERE a.user_id = u.id AND a.status = 'offer'
)
ORDER BY u.full_name;
