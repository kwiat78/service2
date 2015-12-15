from datetime import datetime
import requests

r = requests.get("http://service2-kwiat78.rhcloud.com/api/feeds/loop")
print("[{}] {}".format(datetime.now().isoformat(),r.reason))