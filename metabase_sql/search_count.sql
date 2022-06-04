SELECT  
DATE(published_date) AS "Publish Date",
COUNT(DISTINCT story_id) AS "Number of News Stories Searched",
COUNT(*) AS phrase_count

FROM phrases 

GROUP BY 1
