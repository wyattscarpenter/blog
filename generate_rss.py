#!/usr/bin/env python3

import re
from datetime import datetime
from os.path import basename

def xml_escape(string: str) -> str:
  return string.replace("&","&amp;").replace('"','&quot;').replace("'","&apos;").replace("<","&lt;").replace(">","&gt;") #note that, obviously, &-replacing must come first.

def xml_escape_bytes(string: bytes) -> bytes:
  return string.replace(b"&",b"&amp;").replace(b'"',b'&quot;').replace(b"'",b"&apos;").replace(b"<",b"&lt;").replace(b">",b"&gt;") #note that, obviously, &-replacing must come first.

def xml_cdata_bytes(string: bytes) -> bytes:
  string.replace(b"]]>", b"]]]]><![CDATA[>")
  return b"<![CDATA["+string+b"]]>"

def rss_item(pubDate: str, title_raw: str, link: str) -> bytes:
  # It's kind of implied that the pubDates have to be both time AND date, but we don't really have enough information to do that so we just use the rfc 822 date format https://datatracker.ietf.org/doc/html/rfc822#section-5 (2-digit day 3-letter month 4-digit year) # Actually, we just ignore the RSS specification's specification of rfc 822 format, and use YYYY-MM-DD instead. Who's going to stop us?
  file_name = re.match("^\s*.*?://.*?/blog/(.*?)\s*$", link).group(1) #this regex is fairly flexible to rehosting, but does assume the paths are domain-name-and-maybe-more-stuff/blog/*
  try:
    with open(file_name, "r", encoding="utf-8", newline="\n") as f:
      full_text_raw = f.read()
      full_text = xml_escape_bytes(full_text_raw.encode("utf-8"))
  except UnicodeDecodeError as e: #technically we could just always go the CDATA route from the beginning, but I've arbitrarily chosen to prefer the other way.
    with open(file_name, "rb") as f:
      full_text_raw = f.read()
      full_text = xml_cdata_bytes(full_text_raw)
  return f"""    <item>
      <title>{xml_escape(title_raw)}</title>
      <link>{link}</link>
      <pubDate>{pubDate}</pubDate>
      <guid>{link}</guid>
      <description>""".encode("utf-8") + full_text + b"""</description>
    </item>
"""

version = 2

rss_header = f"""<?xml version="1.0" encoding="UTF-8"?>
<!-- The "UTF-8" encoding of this XML document is slightly misleading, but only slightly; the text is UTF-8, but sometimes has arbitrary binary data included. -->
<rss version="2.0">
  <!-- This rss document was generated by Wyatt S Carpenter's {basename(__file__)} version {version}, using guidance from https://www.rssboard.org/rss-specification , https://www.rssboard.org/files/sample-rss-2.xml , and https://www.rssboard.org/rss-validator/ . -->
  <!-- pubDates are intentionally (if perhaps misguidedly) given here in YYYY-MM-DD format instead of rfc 822 date-time format, in clear defiance of the RSS standard. -->
  <channel>
    <title>Wyatt S Carpenter’s Blog</title>
    <link>https://wyattscarpenter.github.io/blog/</link>
    <description>a programming blog</description>
    <language>en-us</language>
    <lastBuildDate>{datetime.now().astimezone().strftime('%a, %d %b %Y %H:%M:%S %z')}</lastBuildDate> <!-- Note that the timezone information on my development machine is occasionally wrong when I traverse timezones, so this timezone information (though mandatory to provide in the rfc 822 format used in RSS (https://datatracker.ietf.org/doc/html/rfc822#section-5)) should not be trusted too much. -->
"""
rss_footer="""  </channel>
</rss>
"""

with open("rss.xml", "wb") as f:
  f.write(rss_header.encode("utf-8"))
  with open("readme.md", "r", encoding="utf-8") as file:
    for i in file:
      m = re.match("^(.*?): (.*) <?(https?://.*?)>?\s*?$", i) 
      if m:
        f.write( rss_item( *m.groups() ) )
  f.write(rss_footer.encode("utf-8"))
