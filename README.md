# kicad-git-filters
Scripts to make KiCad files more git friendly.

One problem with some KiCad files is that they contain time stamps inside.
It means that every time you generate one of these files you'll get changes,
even when the important content didn't change. This could be very annoying
when using revision tools like *git*.

This isn't really needed if you can trust the time stamp of the files.
When using *git* you can easily find the exact time stamp for a commit.
This is not the same as the time when the file was actually created, but
is quite similar. In projects where this difference is tolerable and
you don't want to commit tons of ridiculous changes you can filter
these time stamps.

This script configures *git* to store the files with a marker instead of
the time stamp. When you check-out the project the markers are replaced
by the actual time stamp. If you need to know the real time stamp you must
consult it using *git*. Note that files that you created mantain the
original time stamp.

# Which files are filtered?

* Gerbers
* Gerber Jobs
* XML BoMs
* BoM CSVs from KiBoM
* BoM HTMLs from KiBoM

# Installation

## Dependencies

This is a Python 3.x script, only standard modules are used.

## Procedure

To install the script run (as root):

```
# make install
```

The scripts will be copied to */usr/local/bin*. If you want to install the scripts in */usr/bin* run


```
# make prefix=/usr install
```

Note: if you are using Debian, or some derived distro like Ubuntu, you can find a Debian package in the releases section.

# Credits and notes

* This script is strongly based on Jesse Vincent [work](https://github.com/obra/kicad-tools).
* I'm not a Python programmer, stackoverflow helps me ... 
