AUTOMAKE_OPTIONS = foreign

SUBDIRS = nvsm_exporters 

release : rpm debian

.PHONY: check-sysconfdir
check-sysconfdir:
	@if [[ "${sysconfdir}" != "/etc" ]] ; then \
		echo -e "ERROR: sysconfdir is NOT set to /etc !!!\n" \
			 "Did you forget to specify --sysconfdir=/etc to ./configure ?" \
		&& false; \
	fi

.PHONY: install_tree
install_tree:
# Create release tree
	rm -rf tmp_pkg_tree
	$(MAKE) install DESTDIR=$(PWD)/tmp_pkg_tree

.PHONY: debian
debian : check-sysconfdir install_tree
# Create release package
	cp -r packaging/DEBIAN tmp_pkg_tree/
	fakeroot dpkg-deb --build tmp_pkg_tree
	dpkg-name --overwrite tmp_pkg_tree.deb

distclean-local :
	find . -name Makefile.in | xargs rm -f
	rm -f config.h.in*
	rm -rf aclocal.m4
	rm -rf autom4te.cache
	rm -rf config m4
	rm -f configure
	rm -rf tmp_pkg_tree/
	rm -rf *.deb
	rm -rf nvsm_exporters/dist
	rm -rf nvsm_exporters/build
	rm -rf nvsm_exporters/*.spec
