import requests,html5lib,json
import boto3,datetime,sys,re

URL = "https://www.sandiegocounty.gov/content/sdc/hhsa/programs/phs/community_epidemiology/dc/2019-nCoV/status.html"

# PDT
date_str = (datetime.datetime.utcnow() - datetime.timedelta(hours=7)).strftime("%Y-%m-%d")

def get_county_html(url=None):
    if not url:
        url = URL
    resp = requests.get(url)
    html = html5lib.parse(resp.content,namespaceHTMLElements=False)
    return html

def parse_out_table(doc):
    data = []
    k = None
    for tr in doc.findall('.//div/table')[0].findall('.//tr'):
        r = [ (e.findall('.//b') and e.findall('.//b')[0].text or e.text)for e in tr.findall('.//td')]
        data.append(r)

    result = {}
    for r in data:
        if len(r) <= 1: continue
        k = r[0]
        v = r[1].strip()
        if not v: continue
        if len(r) == 4:
            v = r[3]
        try:
            v = int(v)
        except ValueError:
            pass
        #print("%s = %s" % (k,v))
        result[k] = v

    result["updated"] = date_str
    return result

if __name__=="__main__":
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else: url = None
    
    htmldoc = get_county_html(url) 
    data = parse_out_table(htmldoc)
    print( json.dumps(data,indent=1) )

def lambda_handler(event, context):
    s3_client = boto3.client('s3')

    path = 'data/corona-sd/coronavirus-latest.json'
    dated_path = 'data/corona-sd/%s-corona-sd.json'
    bucket = 'opensandiego-data'

    # Get Data
    htmldoc = get_county_html() 
    data = parse_out_table(htmldoc)

   # Generate index
    # TODO
    result = s3_client.list_objects_v2(
        Bucket = bucket,
        Prefix = 'data/corona-sd/',
    )
    # Generate listing with date stamp  
    listing = []
    regex = re.compile(r'data\/corona-sd\/(\d+)-(\d+)-(\d+)-corona-sd.json')
    for d in result['Contents']:
        m = regex.match(d['Key'])

        if m:
            datum = json.loads(s3_client.get_object(
                Bucket = bucket,
                Key = d['Key'],
            )['Body'].read())
            listing.append( datum )
    listing.append( data ) 

    # Update full data feed first
    s3_client.put_object( 
        Body = json.dumps(listing,indent=1), 
        Bucket=bucket, 
        Key='data/corona-sd/data.json', 
        ContentType="application/json",
        ACL='public-read',
    )

    # Then put latest snapshot for record keeping
    s3_client.put_object( 
        Body = json.dumps(data,indent=1), 
        Bucket=bucket, 
        Key=path, 
        ContentType="application/json",
        ACL='public-read',
    )
    s3_client.put_object( 
        Body = json.dumps(data,indent=1), 
        Bucket=bucket, 
        ContentType="application/json",
        Key=dated_path % date_str, 
        ACL='public-read',
    )

 
