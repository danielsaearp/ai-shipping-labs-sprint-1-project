import os
import requests
from dotenv import load_dotenv

load_dotenv()

token = os.environ.get("GITHUB_TOKEN")

headers = {
    "Accept": "application/vnd.github+json",
}

if token:
    headers["Authorization"] = f"Bearer {token}"


page=1
all_issues=[]

while True:
    # if page == 2:
    #   url = "https://api.github.com/repos/apache/this-repo-does-not-exist/issues"
    # else:
    #   url = "https://api.github.com/repos/apache/airflow/issues"
    url = "https://api.github.com/repos/apache/airflow/issues"
    params={
          "state": "open",
          "per_page": 100,
          "sort": "created",
          "direction": "desc",
          "page": page,
      }
    
    try:
        r=requests.get(url
            , params=params, headers=headers,     )
        r.raise_for_status()
    except Exception as e:
        print(e)
        break

    for item in r.json():
        if "pull_request" not in item:
            all_issues.append(item)
   
    if "next" not in r.links:
        print("end of the loop")
        break
    else:
        print("has next")
    page = page + 1
print(len(all_issues))
print(page)
 
    
# print(page)
# print(len(all_issues))
# print(all_issues[0])



#print(r.links)

#print(r.json())

#print(r.links['next'])

#print(r.json())

#r=r.json()

#pull_requests = [r[i] for i in range(0,len(r)) if "pull_request" in r[i].keys()]

#issues = [r[i] for i in range(0,len(r)) if "pull_request" not in r[i].keys()]


#print(len(pull_requests), len(issues))

#print(type(r[0]))

#print(r[0].keys())

#print(1 if "pull_request" in r[0].keys() else 0)
#if "pull_request" in r[0].keys() then print 1 else 2


#print(type(json.loads(r[0])))

#print(type(r.json()))

#print(json.dumps(r.json()))
#type(json.dump(r.json(),file))

#with open('src/example_1.json', 'w') as file:
 #   json.dump(r.json(),file, indent=2)


#print(type(r))
#print(r.json())