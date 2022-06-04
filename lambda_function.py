# import libraries
import urllib.parse,io,json,datetime as dt,random,boto3,http.client,os
import pandas as pd,mysql.connector

# connect to S3 and DB
def setup():
    s3 = boto3.client('s3',aws_access_key_id=os.environ['ACCESS_KEY_ID'],aws_secret_access_key=os.environ['SECRET_ACCESS_KEY'])
    today = dt.datetime.utcnow().date()
    config = {'user':os.environ['USER'],'password':os.environ['PASSWORD'],'host':os.environ['HOST'],'database':os.environ['DATABASE']}
    conn = mysql.connector.connect(**config)
    cur = conn.cursor()
    params = urllib.parse.urlencode({'access_key':os.environ['API_ACCESS_KEY'],'languages': 'en','sort': 'published_desc','limit': 100,'date': str(today)})
    bucket = 's3://'+os.environ['BUCKET']+'/'
    print('setup done')
    return s3,today,conn,cur,params,bucket

# pull news stories that have already been processed and stored in the S3 bucket
def pull_seen_stories(s3,today,bucket):
    try:
        data = s3.get_object(Bucket=os.environ['BUCKET'],Key=str(today)+'_seen.csv') 
    except:
        seen_stories = pd.DataFrame(columns=['published_date','title','description'])
    else: 
        seen_stories = pd.read_csv(io.StringIO(data['Body'].read().decode()),sep=',')
    print('SEEN stories: '+str(len(seen_stories)))
    return seen_stories

# get new stories that have not been processed by pulling recent stories and comparing them to the ones stored in the bucket
def get_new_stories(s3,today,params,seen_stories,bucket):
    extracted_stories = pd.DataFrame(columns=['published_date','title','description'])
    newsapi = http.client.HTTPConnection('api.mediastack.com')
    newsapi.request('GET','/v1/news?{}'.format(params))
    res = newsapi.getresponse().read()
    extracts = json.loads(res.decode('utf-8'))['data']
    for extract in extracts:
        published_date = dt.datetime.strptime(extract['published_at'],'%Y-%m-%dT%H:%M:%S+00:00').date()
        title = extract['title'].replace('\'','').replace('\"','')
        description = extract['description'].replace('\'','').replace('\"','')
        extracted_stories = extracted_stories.append({'published_date':published_date,'title':title,'description':description},ignore_index=True)
    extracted_stories = extracted_stories.fillna(value=' ').drop_duplicates()
    extracted_stories.to_csv(bucket+str(today)+'_extracted.csv',index=False)
    data = s3.get_object(Bucket=os.environ['BUCKET'],Key=str(today)+'_extracted.csv')
    extracted_stories = pd.read_csv(io.StringIO(data['Body'].read().decode()),sep=',')

    merged = extracted_stories.merge(seen_stories,how='left',on=['published_date','title','description'],indicator=True)
    new_stories = merged[merged['_merge']=='left_only']
    new_stories = new_stories.drop(columns=['_merge']).fillna(value=' ').drop_duplicates()
    new_stories.to_csv(bucket+str(today)+'_new.csv',index=False)
    data = s3.get_object(Bucket=os.environ['BUCKET'],Key=str(today)+'_new.csv')
    new_stories = pd.read_csv(io.StringIO(data['Body'].read().decode()),sep=',')
    print('NEW stories: '+str(len(new_stories)))
    return new_stories

# break the new stories into phrases and send them to Aurora
def send_phrases_to_aurora(today,cur,new_stories,bucket):
    common = ['how','will','at','of','in','on','the','as','a','and','by','is','are','no','not','to','for','from']
    for index,row in new_stories.iterrows():
        story_id = random.randint(1,1000000000)
        words = row['title'].replace('.','').replace(',','').lower().split()+row['description'].replace('.','').replace(',','').lower().split()
        values = ''
        for i in range(len(words)-1): #2 word phrases
            if words[i] not in common and words[i+1] not in common:
                values = values+'(\''+str(today)+'\','+str(story_id)+',\''+words[i]+' '+words[i+1]+'\'),'
        for i in range(len(words)-2): #3 word phrases
            if words[i] not in common or words[i+1] not in common or words[i+2] not in common:
                values = values+'(\''+str(today)+'\','+str(story_id)+',\''+words[i]+' '+words[i+1]+' '+words[i+2]+'\'),'
        for i in range(len(words)-3): #4 word phrases
            if words[i] not in common or words[i+1] not in common or words[i+2] not in common or words[i+3] not in common:
                values = values+'(\''+str(today)+'\','+str(story_id)+',\''+words[i]+' '+words[i+1]+' '+words[i+2]+' '+words[i+3]+'\'),'
        values = values[:-1]
        cur.execute('INSERT IGNORE INTO phrases(published_date,story_id,phrase) VALUES'+values+';')
    print('updated phrases table in aurora')

# add the new stories that have just been processed to the S3 bucket, and then end the program by commiting the changes made to Aurora
def close(today,cur,conn,seen_stories,new_stories,bucket):
    updated_seen_stories = seen_stories.append(new_stories)
    updated_seen_stories.to_csv(bucket+str(today)+'_seen.csv',index=False)
    conn.commit()
    cur.close()
    conn.close()
    print('SEEN stories now: '+str(len(updated_seen_stories)))

# run the program using lambda function
def lambda_handler(event,context):
    s3,today,conn,cur,params,bucket = setup()
    seen_stories = pull_seen_stories(s3,today,bucket)
    new_stories = get_new_stories(s3,today,params,seen_stories,bucket)
    send_phrases_to_aurora(today,cur,new_stories,bucket)
    close(today,cur,conn,seen_stories,new_stories,bucket)
    return {'statusCode': 200}