cron.py
=====
cron.py is small cron-like scheduler designed for simple, recurring jobs. It supports a basic set of field values though is extensible by using any class inheriting from `cron.Field`.

Usage
-----
Below is basic usage for printing a message every hour.

```
import cron

scheduler = cron.Scheduler()
scheduler.add(cron.Job(print, [ 'Hourly function, run every hour!' ], minute=0))
scheduler.add(cron.Job(print, [ 'This one runs every 20 minutes!' ], minute=cron.Every(20)))
scheduler.start()
```
