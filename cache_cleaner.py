import os
import datetime

cachedir = '/srv/lebedev/cache'
thr = datetime.timedelta(days=2)

now = datetime.datetime.now()

for img in os.listdir(cachedir):

    ts = os.stat(cachedir + os.sep + img).st_mtime
    create_time = datetime.datetime.utcfromtimestamp(ts)

    if datetime.datetime.now() - create_time >= thr:
        os.unlink(cachedir + os.sep + img)
