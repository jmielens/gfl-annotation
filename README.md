# gfl-annotation
A local annotation interface for FUDG/GFL.

## Basic Usage ##

* Start the interface by running `python gflAnnoInterface/interface.py -s testSents` in the root directory.
* Select `Next` to begin annotating.
* Navigate sentences using the `Next` and `Prev` buttons.
* When finished, select `File > Dump Annotations` to output the annotations to the JSON file (default out.json)

## Errors ##

* Use the `Check` button to check the current annotation for errors. If errors occur the bar will turn red.
* To correct an error, press the `Undo` button to return the annotation to its last good state.
