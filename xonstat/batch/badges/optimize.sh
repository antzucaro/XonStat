#!/bin/sh -e
# Optimize png files in output directory

find output -name "*.png" | while read png; do
	# Reduce colors to 8bit
	# <http://pngquant.org>
	pngquant --skip-if-larger --force --output "$png" 256 "$png"

	# Adjust bit depth, remove clutter
	# <http://optipng.sourceforge.net>
	optipng -o 1 -strip all "$png"

	# Compress with zopfli
	# <http://www.advancemame.it>
	#advpng -z -4 "$png"
done
