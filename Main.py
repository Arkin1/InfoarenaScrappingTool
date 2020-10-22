from InfoarenaScrapper import InfoarenaScrapper

isc = InfoarenaScrapper()

isc.get_problems_links(300)
isc.collect_sourcecode_urls()
