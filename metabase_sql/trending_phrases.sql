SELECT 
t1.phrase,
t1.used_count

FROM
(
    SELECT
    phrase AS phrase, 
    COUNT(DISTINCT story_id) AS used_count
    FROM phrases 
    WHERE published_date = current_date() AND phrase NOT REGEXP '[&)]' AND phrase NOT REGEXP 'inc'
    GROUP BY 1
) t1 
LEFT JOIN 
(
    SELECT
    phrase AS Phrase, 
    COUNT(DISTINCT story_id) AS used_count
    FROM phrases 
    WHERE published_date >= current_date() - INTERVAL 6 DAY
    AND phrase NOT REGEXP '[&)]' AND phrase NOT REGEXP 'inc'
    GROUP BY 1
    ORDER BY 2 DESC
    LIMIT 100
) t2 ON t1.phrase = t2.phrase

WHERE t2.phrase is null

ORDER BY 2 DESC  
LIMIT 30

