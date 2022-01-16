# drun
A simple way to run applications that use a TUI, but you want to run them in the background, without losing access to the TUI, for example a minecraft server
## drun.py
```sh
$ drun.py -s ./socket sh
```
listens to the domain socket ./socket, waiting for arun.py to provide input. Outputs a transcript of the interaction to stdout. Does not read stdin. Only one arun.py can be connected at a time.
## arun.py
```sh
$ arun.py -s ./socket
```
connects to the ./socket and provides a (for now kind of poor) access to the TUI of the process drun is running. to detach, simply press ctrl+C. If you want to stop the interior process, either SIGINT drun.py, or use an internal command of the TUI.

## final notes
This projects is heavily untested, so it may very well not work for your usecase.