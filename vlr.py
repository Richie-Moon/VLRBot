import datetime

string = '3d 11h ago'

time_now = datetime.datetime.now()
string = string.split()

string.pop(-1)
print(string)

for item in string:
    if item[1] == 'w':
        time_now -= datetime.timedelta(weeks=float(item[0]))
    elif item[1] == 'd':
        time_now -= datetime.timedelta(days=float(item[0]))
    elif item[1] == 'h':
        time_now -= datetime.timedelta(hours=float(item[0]))
    elif item[1] == 'm':
        time_now -= datetime.timedelta(minutes=float(item[0]))
    elif item[1] == 's':
        time_now -= datetime.timedelta(seconds=float(item[0]))

print(time_now)


unix = int(datetime.datetime.strptime(str(time_now.date()), '%Y-%m-%d').timestamp())

print(unix)
