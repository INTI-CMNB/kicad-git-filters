#!/usr/bin/make
prefix=/usr/local

all:

install:
	install -D kicad-git-filters.py $(DESTDIR)$(prefix)/bin/kicad-git-filters.py

clean:

distclean: clean

uninstall:
	-rm -f $(DESTDIR)$(prefix)/bin/kicad-git-filters.py

deb:
	fakeroot dpkg-buildpackage -uc -b

debclean:
	fakeroot debian/rules clean


.PHONY: all install clean distclean uninstall deb

