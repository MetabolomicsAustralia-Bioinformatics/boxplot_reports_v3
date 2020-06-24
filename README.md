# Boxplot Reporting Script

* Script to produce a multi-page pdf of boxplots.
* No exotic requirements, though `matplotlib`'s multi-page pdf looks rather brittle.
* Clean, stable-working version kept here for posterity (and for maintenance)

### Set Up

```
# create virtual env named venv
python3 -m venv venv
# install requirements
pip3 install requirements.txt
# Activate virtual env
source venv/bin/activate
# Start local server
python3 app.py
```


### To Do

* Title fontsize adjustment: how to double-line for super-long titles?
* Automatic log-median normalization?
* Some linting if necessary (none so far).
