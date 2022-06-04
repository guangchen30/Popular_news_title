# Popular News Headlines

The aim of this project is to build a live dashboard showing the most frequently used phrases in news headlines to see if any useful insights into recents trends can be gained. This is done by building a data pipeline in python that pulls live news data from [Mediastack API](https://mediastack.com) and processes the data using python and SQL.

# Architecture
![Arch](architecture.jpg)
 
- The Mediastack API provides an HTTP GET endpoint that delivers live news data in JSON format.
- The python script is scheduled to run every 5 mins by Lambda to pull all the latest news data, from which the script extracts the title and description of each news story and transforms them into phrases. The transformation is done by grouping each word with up to 3 subsequent words together (limited words to reduce complexity).
- The script then loads the phrase data into Aurora DB so that BI tools like Metabase, can access and turn the data into visualisations.
- Process the data further by running SQL queries inside Metabase and create the dashboard below


# Live Dashboard (URL)




# Comments/conclusions
- 
