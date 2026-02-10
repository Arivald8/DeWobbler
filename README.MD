> _Dewobbler (n.): A tool designed to identify, correct, or eliminate instability, errors, or erratic behavior ("wobbles") within a system._

Dev notes:

On sys.remote_exec (https://docs.python.org/3/library/sys.html#sys.remote_exec)

The code is executed by the target process's main thread.

The caller must make sure that the file exists whenever the remote process tries to read it.

The remote process MUST be running a CPython interpreter of the same major and minor version as the local process, including pre-release versions.

When the code is executes in the remote process, an auditing event sys.remove_exec is raised with the pid and the path to the scrip file. This event is raised in the 
process that called sys.remote.exec()

When the script is executed in the remote process, an auditing event cpython.remote_debugger_script is raised with the path in the remote process.


