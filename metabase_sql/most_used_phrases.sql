SELECT
phrase AS Phrase, 
COUNT(DISTINCT story_id) AS "Number of stories used on"

FROM phrases 
WHERE published_date = current_date()
AND phrase NOT REGEXP '[&)]' AND phrase NOT REGEXP 'inc'

GROUP BY 1
ORDER BY 2 DESC  
LIMIT 30
