"""Command execution"""

import io
import select
import subprocess
import sys

from progfiguration import logger


class MagicPopen(subprocess.Popen):
    """A subprocess.Popen with superpowers

    This is a wrapper for subprocess.Popen,
    which is guaranteed to have a .stdout and .stderr property,
    which will always be StringIO objects (not bytes).

    It's the return value for magicrun(),
    and shouldn't be used elsewhere.
    """

    stdout: io.StringIO
    stderr: io.StringIO


def magicrun(cmd: str | list, print_output=True, log_output=False, check=True, *args, **kwargs) -> MagicPopen:
    """Run a command, with superpowers

    Params:

    * `cmd`: The command to run. If a string, it will be passed to a shell.
    * `print_output`: Print the command's stdout/stderr in to the controlling terminal's stdout/stderr in real time.
        stdout/stderr is always captured and returned, whether this is True or False (superpowers).
        The .stdout and .stderr properties are always strings, not bytes
        (which is required because we must use universal_newlines=True).
        * <https://gist.github.com/nawatts/e2cdca610463200c12eac2a14efc0bfb>
        * <https://stackoverflow.com/questions/4417546/constantly-print-subprocess-output-while-process-is-running>
    * `log_output`: Log the command's stdout/stderr in a single log message (each) after the command completes.
    * `check`: Raise an exception if the command returns a non-zero exit code.
        Unlike subprocess.run, this is True by default.
    * `*args, **kwargs`: Passed to subprocess.Popen
        Do not pass the following arguments, as they are used internally:
        * shell: Determined automatically based on the type of cmd
        * stdout: Always subprocess.PIPE
        * stderr: Always subprocess.PIPE
        * universal_newlines: Always True
        * bufsize: Always 1

    A `MagicPopen` object is always returned.
    """
    shell = isinstance(cmd, str)

    logger.debug(f"Running command: {cmd}")

    # ignore mypy errors because *args and **kwargs confuses it
    process = subprocess.Popen(  # type: ignore
        cmd,
        shell=shell,
        bufsize=1,  # Output is line buffered, required to print output in real time
        universal_newlines=True,  # Required for line buffering
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        *args,
        **kwargs,
    )

    stdoutbuf = io.StringIO()
    stderrbuf = io.StringIO()

    # Ignore mypy errors related to stdout/stderrbuf not being file objects.
    # We know they're file objects because we set them to subprocess.PIPE.

    stdout_fileno = process.stdout.fileno()  # type: ignore
    stderr_fileno = process.stderr.fileno()  # type: ignore

    # This returns None until the process terminates
    while process.poll() is None:

        # select() waits until there is data to read (or an "exceptional case") on any of the streams
        readready, writeready, exceptionready = select.select(
            [process.stdout, process.stderr],
            [],
            [process.stdout, process.stderr],
            0.5,
        )

        # Check if what is ready is a stream, and if so, which stream.
        # Copy the stream to the buffer so we can use it,
        # and print it to stdout/stderr in real time if print_output is True.
        for stream in readready:
            if stream.fileno() == stdout_fileno:
                line = process.stdout.readline()  # type: ignore
                stdoutbuf.write(line)
                if print_output:
                    sys.stdout.write(line)
            elif stream.fileno() == stderr_fileno:
                line = process.stderr.readline()  # type: ignore
                stderrbuf.write(line)
                if print_output:
                    sys.stderr.write(line)
            else:
                raise Exception(f"Unknown file descriptor in select result. Fileno: {stream.fileno()}")

        # If what is ready is an exceptional situation, blow up I guess;
        # I haven't encountered this and this should probably do something more sophisticated.
        for stream in exceptionready:
            if stream.fileno() == stdout_fileno:
                raise Exception("Exception on stdout")
            elif stream.fileno() == stderr_fileno:
                raise Exception("Exception on stderr")
            else:
                raise Exception(f"Unknown exception in select result. Fileno: {stream.fileno()}")

    # Check for any remaining output after the process has exited.
    # Without this, the last line of output may not be printed,
    # if output is buffered (very normal)
    # and the process doesn't explictly flush upon exit
    # (also very normal, and will definitely happen if the process crashes or gets KILLed).
    for stream in [process.stdout, process.stderr]:
        for line in stream.readlines():
            if stream.fileno() == stdout_fileno:
                stdoutbuf.write(line)
                if print_output:
                    sys.stdout.write(line)
            elif stream.fileno() == stderr_fileno:
                stderrbuf.write(line)
                if print_output:
                    sys.stderr.write(line)

    # We'd like to just seek(0) on the stdout/stderr buffers, but "underlying stream is not seekable",
    # So we create new buffers above, write to them line by line, and replace the old ones with these.
    process.stdout.close()  # type: ignore
    stdoutbuf.seek(0)
    process.stdout = stdoutbuf
    process.stderr.close()  # type: ignore
    stderrbuf.seek(0)
    process.stderr = stderrbuf

    if check and process.returncode != 0:
        msg = f"Command failed with exit code {process.returncode}: {cmd}"
        logger.error(msg)
        logger.info(f"stdout: {process.stdout.getvalue()}")
        logger.info(f"stderr: {process.stderr.getvalue()}")
        raise Exception(msg)

    logger.info(f"Command completed with return code {process.returncode}: {cmd}")

    # The user may have already seen the output in std out/err,
    # but logging it here also logs it to syslog (if configured).
    if log_output:
        # Note that .getvalue() is not (always?) available on normal Popen stdout/stderr,
        # but it is available on our StringIO objects.
        # .getvalue() doesn't change the seek position.
        logger.info(f"stdout: {process.stdout.getvalue()}")
        logger.info(f"stderr: {process.stderr.getvalue()}")

    # Now that we've set stdout/err to StringIO objects,
    # we can return the Popen object as a MagicPopen object.
    magic_process: MagicPopen = process

    return magic_process
