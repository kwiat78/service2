from datetime import datetime
import requests


start = datetime.now()
x = requests.get("http://service2-kwiat78.rhcloud.com/api/feeds/loop")
print("[{}] {} {} {}".format(datetime.now().isoformat(),x.json(),x.reason,(datetime.now()-start).microseconds))