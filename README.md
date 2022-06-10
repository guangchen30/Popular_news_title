# Popular News Headlines

The aim of this project is to build a live dashboard showing the most frequently used phrases in news headlines to see if we can gain any useful insights into recents trends from observing such data. This is done by building a data pipeline in python that pulls live news data from [Mediastack API](https://mediastack.com) and building a dashboard on Redash to visualise the data.

# Architecture
![Arch](architecture.jpg)
 
- The Mediastack API provides an HTTP GET endpoint that delivers live news data in JSON format.
- The [python script](lambda_function.py) is scheduled to run every 5 mins by Lambda to pull all the latest news data, from which the script extracts the title and description of each news story and transforms them into phrases. The transformation is done by grouping each word with up to 3 subsequent words together (limited words to reduce complexity).
- The script then loads the phrase data into a MySQL DB (Aurora). OLAP databases like Snowflake and Redshift would be more suitable for the analytical queries that will be running on Redash, but for this project it is unlikely that more than 5 million rows will need to be processed by any single query. Therefore, a small Aurora instance will be sufficient and ideal for this project to minise the running costs. 
- Run [SQL queries](/sql) on Redash to extract the data from Aurora and process it further to create the dashboard below.


# [Live Dashboard](http://ec2-18-183-79-50.ap-northeast-1.compute.amazonaws.com/public/dashboards/iDdhUeO0K6MzT2izcGGaFqDlPOnl6gR3mIYSajl9?org_slug=default&p_w3_Search%20this%20phrase=stock%20market)

- This dashboard gets populated with the latest data every hour
- The dashboard shows the total numbers of news headlines and phrases collected each day, as well as today's most trending phrases and this week's most popular phrases

# Comments/conclusions
- Most of the top phrases are only frequently used because they are very common the English language, not because they are trending, making it difficult to separate them from real trending phrases.
- Also, analysing 2 to 4 word phrases may not be a good idea since they are too short to convey any useful information
