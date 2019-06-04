dnl Process this file with autoconf to produce a configure script.

AC_INIT(hrgrest, 0.1)
AC_SUBST(version, AC_PACKAGE_VERSION)
AC_SUBST(tarname, AC_PACKAGE_TARNAME)

AC_CONFIG_AUX_DIR(config)

AC_CONFIG_HEADERS(config.h)

AC_PREFIX_DEFAULT([/usr/])

AM_INIT_AUTOMAKE([foreign subdir-objects])

AM_EXTRA_RECURSIVE_TARGETS([includepaths])

AC_PROG_CC

AC_PROG_CXX

AC_PROG_GO

AM_PROG_AS

AM_PROG_AR

AC_CHECK_TOOL([OBJCOPY], [objcopy])
AC_CHECK_TOOL([SIZE], [size])

dnl AS_IF([test x$sysconfdir = x'${prefix}/etc'], [sysconfdir=/etc])

AC_PROG_RANLIB

AC_CONFIG_FILES(
	Makefile
	nvsm_exporters/Makefile
	packaging/DEBIAN/control
)

AC_OUTPUT

