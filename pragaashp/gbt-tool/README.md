# gbt-tool

Tool to isolate observable targets (from a database) using times scraped from the GBT Schedule.

**Update:** 

  - Uses multiprocessing to allow up to 1.7x speedup over previous version.
  - Supports connecting to remote database server over ssh-tunnel.

**Pre-requisites:**

  - <a href="http://continuum.io/downloads">Anaconda</a> distribution.
  - Astoplan package: `pip install astroplan`
  - SQLAlchemy package: `pip install SQLAlchemy`
  - Astropy package: `pip install astropy`

**SSH Tunneling:**  

For the script to run on the local machine, setup a ssh-tunnel on port 3307 to the remote server with the MySQL database: `ssh -L 3307:127.0.0.1:3306 `*`username@remote_host`*.

> Note: `3307:localhost:3306` will not work due to how MySQL establishes connections through networks.

**Usage:**

*Terminal*

  - Add more `constraints` in the `"__main__"` section.
  
    > If required, `import` from `astroplan` more `Constraint` modules.

  - Run the script: `$ python gbt.py` from the terminal and view results in a browser.

*Script/Interpreter*

  - Begin by `import`ing the class: `from gbt import *`.
  - Create a `constraints` list e.g.:
  
    > `constraints = [AltitudeConstraint(40*u.deg,80*u.deg), SunSeparationConstraint(20*u.deg)]`.

  - Initialize the tool with `constraints`: `tool = GBTObservables(constraints)`.
  - Generate table of observable targets for `n`-th schedule (*zero-endexed*): `table = tool.getTargets(n)`.
  
  - Get information about scheduled observation: `tool.viewSchedule(n)` or confirm schedule for current table:
    
    > `table.meta['start_time']` and `table.meta['end_time']`.
  
  - View table in browser: `table.show_in_browser(jsviewer=True)`
