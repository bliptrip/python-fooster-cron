cron.py
=====
cron.py is small cron-like scheduler designed for simple, recurring jobs. It supports a basic set of field values though is extensible by using any class inheriting from `cron.Field`.

Usage
-----
Below is basic usage for calling a function and printing a message every hour (at minute 0), a set of minutes every hour, and every 20 minutes per hour.

```python
import cron

def count():
	for i in range(5):
		print(i)

scheduler = cron.Scheduler()
scheduler.add(cron.Job(count, minute=5))
scheduler.add(cron.Job(print, [ 'Hourly function, run every hour on the hour!' ], name='hourly', minute=0))
scheduler.add(cron.Job(print, [ 'This one runs at special minutes!' ], minute=[ 1, 2, 3, 5, 8, 13, 21, 34, 55 ]))
scheduler.add(cron.Job(print, [ 'This one runs every 20 minutes within each hour!' ], minute=cron.Every(20)))
scheduler.start()
```

### cron.Job
Prototype:
```python
cron.Job(function, args=[], kwargs={}, name=None, minute=cron.All(), hour=cron.All(), day=cron.All(), month=cron.All(), weekday=cron.All())
```

Attributes:
| Attribute | Value                                  |
| --------- | -------------------------------------- |
| function  | function to call                       |
| args      | list of function arguments             |
| kwargs    | dictionary of named function arguments |
| minute    | range [0, 59]                          |
| hour      | range [0, 23]                          |
| day       | range [1, 31]                          |
| month     | range [1, 12]                          |
| weekday   | range [0, 6], 0 is Monday              |


### cron.Field
To make a custom field, inherit from `cron.Field` and change the `__eq__` method to return `True` when the passed value matches. The param member of the class is automatically populated with the passed argument unless the `__init__` method is overridden. The value passed is a value from one of the `time.struct_time` fields.

#### Examples

##### List
```python
class List(cron.Field):
	def __eq__(self, value):
		return value in self.param
```
##### All
```python
class All(cron.Field):
	def __init__(self):
		pass

	def __eq__(self, value):
		return True
```
