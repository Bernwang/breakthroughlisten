# gbt-tool

Tool to isolate observable targets (from a database) using times scraped from the GBT Schedule.

**Update:** 

  - Script updated to utilize Multiprocessing to allow up to 1.7x speedup over previous version.

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
