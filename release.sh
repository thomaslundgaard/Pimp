#!/bin/sh

pkgname="pympdjuke"
pkgver="$1"
pkgfullname="$pkgname-$pkgver"

# check arguments and that the correct git commit is checked out
if [ ! "$1" ]; then
	echo "Package version to be released not specified"
	echo "Usage: $0 PKGVER"
	exit 1
fi

if [ "$(git rev-parse HEAD)" != "$(git rev-parse $pkgver)" ]; then
	echo "Your HEAD is not currently tagged as $pkgver"
	echo "Either do a 'git checkout $pkgver' or a 'git tag $pkgver'"
	exit 1
fi

if [ "$(git diff HEAD)" ]; then
	echo "Your working tree is dirty"
	echo "Commit or stash you local changes"
	exit 1
fi

# copy files into a .tar.bz2
mkdir "$pkgfullname"
make clean
cp -r pixmaps resources src LICENSE Makefile pympdjuke.desktop README "$pkgfullname"
tar -cvv --bzip2 -f "$pkgfullname.tar.bz2" "$pkgfullname"
rm -rf "$pkgfullname"

# create .deb package

