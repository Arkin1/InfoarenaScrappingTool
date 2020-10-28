from InfoarenaScrapper import *

isc = InfoarenaScrapper()

isc.get_problems_links(300)
isc.collect_sourcecode_urls("problems.data", "probleme_rezolvate")
isc.collect_urls_arhiva("arhiva_probleme.data")
isc.collect_sourcecode_urls("arhiva_probleme.data", "arhiva_educationala")