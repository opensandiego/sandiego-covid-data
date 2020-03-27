import requests,html5lib,json
import boto3


def get_county_html():
    URL = "https://www.sandiegocounty.gov/content/sdc/hhsa/programs/phs/community_epidemiology/dc/2019-nCoV/status.html"
    resp = requests.get("https://www.sandiegocounty.gov/content/sdc/hhsa/programs/phs/community_epidemiology/dc/2019-nCoV/status.html")
    html = html5lib.parse(resp.content,namespaceHTMLElements=False)
    return html

def parse_out_table(doc):
    data = []
    k = None
    for tr in doc.findall('.//table')[0].findall('.//tr'):
        r = [ e.text for e in tr.findall('.//td/b')]
        if not r or r[0] == None:
            r =  [k] + [ e.text for e in tr.findall('.//td')]
            data.append(r)
        else:
            k = r[0]
            if len(r) > 1:
                data.append(r)

    result = {}
    for r in data:
        if len(r) == 2 and r[0]:
            result[r[0]] = r[1] 
        elif len(r) == 3:
            result.setdefault(r[0],{})
            result[r[0]][r[1]] = int(r[2])
    return result

if __name__=="__main__":
    htmldoc = get_county_html() 
    data = parse_out_table(htmldoc)
    print( json.dumps(data,indent=1) )

def lambda_handler(event, context):
    s3_client = boto3.client('s3')

    path = 'data/coronavirus-latest.json'
    bucket = 'opensandiego-data'

    # Get Data
    htmldoc = get_county_html() 
    data = parse_out_table(htmldoc)
    s3_client.put_object( Body = json.dumps(data,indent=1), Bucket=bucket, Key=path )

