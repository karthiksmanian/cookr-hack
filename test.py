import requests
from bs4 import BeautifulSoup
diff_url = "https://patch-diff.githubusercontent.com/raw/karthiksmanian/cookr-hack/pull/3.diff?token=ASFR2KZ4L6MEH6J2G6BPG5TF36ML4"
r = requests.get(diff_url)
soup = BeautifulSoup(r.content,'html5lib')

print(r,soup)

