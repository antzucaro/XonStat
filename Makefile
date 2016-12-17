css:
	cd xonstat/static/css && cat foundation.css font-awesome.css app.css luma.css > combined.css
	yuicompressor --type css -o xonstat/static/css/xonstat.css xonstat/static/css/combined.css
	rm xonstat/static/css/combined.css
