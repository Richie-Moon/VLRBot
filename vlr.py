import datetime

dt_now = datetime.datetime.now()
string = ['3d 11h from now', '14h 19m ago']

a = datetime.datetime(100, 1, 1, 11, 34, 59)
b = a + datetime.timedelta(0, 3)  # days, seconds, then other fields.
print(a)
print(b)
