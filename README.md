# parsley
python filesystem synchronization

Read README.pdf!

Parsley keeps a configured set of places in file systems in sync on a regular basis.

Those file systems can live on remote machines and become mounted
by means of sshfs at runtime automatically.

Features:

- Keeps local and ssh file systems in sync
- Has a mechanism for metadata synchronization (tags, rating, ...)
- Robust infrastructure with working retry and error handling
- Alternative modes
 - move to sink mode: always moves all files from the source to a sink and so keep the source empty.
- Flexible and extensible api
