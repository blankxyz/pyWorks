from xml.dom.minidom import parse
import xml.dom.minidom

#https://www.youtube.com/feeds/videos.xml?channel_id=UC7V6hW6xqPAiUfataAZZtWA
DOMTree = xml.dom.minidom.parse("feed.xml") #Android Police
collection = DOMTree.documentElement

published = collection.getElementsByTagName("published")
for i in range(len(published)):
    print published[i].childNodes[0].data