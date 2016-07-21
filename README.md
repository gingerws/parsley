# parsley
python filesystem synchronization

Dear Friend, this isn't a github project anymore. Please visit the project homepage: https://pseudopolis.eu/wiki/pino/projs/parsley/

Parsley keeps a configured set of places in file systems in sync.

Features:

- Keeps configured file system places in sync (local and ssh)
- Robust infrastructure with working retry and error handling
- Customizable behavior with the availability to add additional program logic for various situations
- Optional 'move to sink mode': always moves all files from the source to a sink and so keep the source empty
- Has a mechanism for metadata synchronization (tags, rating, ...)
- Can be used stand-alone or embedded in other tools with a flexible and extensible api
- Rich graphical interface for configuration and for executing synchronization
- Graphical interface for manually resolving conflicts which occurred in a synchronization run
- Designed for being driven by a scheduled task (a.k.a. cronjob), which executes a background command (e.g. each minute)
- In background mode: Own handling of synchronization intervals (independent of the interval for the scheduled task)
