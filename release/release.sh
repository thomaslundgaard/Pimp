#!/bin/sh
pkgname="pympdjuke"
tmpdir="release-tmp"
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
	echo "Commit or stash your local changes"
	exit 1
fi

mkdir "$tmpdir"
cd "$tmpdir"

# copy files into a .tar.bz2
mkdir "$pkgfullname"
cd ..
make clean
cp -r pixmaps icons resources src LICENSE Makefile pympdjuke.desktop README "$tmpdir/$pkgfullname"
cd "$tmpdir"
tar -c --bzip2 -f "../release/$pkgfullname.tar.bz2" "$pkgfullname"

# create PKGBUILD for archlinux AUR
cp "../release/PKGBUILD.template" "PKGBUILD"
md5sum="$(md5sum "../release/$pkgfullname.tar.bz2" | cut -f1 -d' ')"
sed -i "s;pkgver=;pkgver=$pkgver;g" "PKGBUILD"
sed -i "s;md5sums=();md5sums=($md5sum);g" "PKGBUILD"
cp "../release/$pkgfullname.tar.bz2" .
makepkg --source
mv "$pkgfullname-1.src.tar.gz" "../release/$pkgfullname-1-aur.tar.gz"

cd ..
rm -r "$tmpdir"

