from xml.etree import ElementTree

with open('E654390.XML', 'rt') as f:
    tree = ElementTree.parse(f)

logfile = open("log_Item.txt", "w")

for node in tree.iter('Item'):
    #print node.tag, node.attrib
    
    uid = node.attrib.get('UID')
    sid = node.attrib.get('SID')
    psn = node.attrib.get('PSN')
    
    logfile.write(uid)
    logfile.write("\t")
    logfile.write(sid)
    logfile.write("\t")
    logfile.write(psn)
    logfile.write("\n")
    
logfile.close()

with open('E654390.XML', 'rt') as f:
    tree = ElementTree.parse(f)

logfile = open("log_SummaryItem.txt", "w")

for node in tree.iter('SummaryItem'):
    
    sid = node.attrib.get('SID')
    psn = node.attrib.get('PSN')
    
    logfile.write(sid)
    logfile.write("\t")
    logfile.write(psn)
    
    for i in range(len(node)):
        logfile.write("\n")
        logfile.write("\t")
        logfile.write("\t")
        logfile.write(node[i].tag + '=' + node[i].text)
    
    logfile.write("\n")
    
logfile.close()