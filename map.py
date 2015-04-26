import xml.etree.ElementTree as ET
import pprint
import re
import codecs
import json
"""
"""

lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')
addpat = re.compile(r'addr:(\w+)(:\w*)*')
namepat = re.compile(r'name:(\w+)(:\w*)*')

CREATED=["version","changeset","timestamp","user","uid"]
POS=["lat","lon"]
MISC=["id","visible","amenity","cuisine","phone"]
ELETAGS=["tag", "meta" , "bounds", "note", "nd", "member", "relation", "osm"]

nottags={}
out2=open('mapothertags.txt', 'w')

def shape_element(element):
    node = {}
    if element.tag == "node" or element.tag == "way":
        # YOUR CODE HERE
        node = {'created':{}, 'type':element.tag}
        for ele in element.attrib:
          #positional parameters
          if ele in POS:
            continue
          #parameters in created structure
          elif ele in CREATED:
            node['created'][ele]=element.attrib[ele]
          #all others
          elif ele in MISC:
            node[ele]=element.attrib[ele]
          #if aborted, add new one into list
          else:
            sys.exit(element.attrib[ele])
        #there's no test for existence
        try:
          node['pos']=[float(element.attrib['lat']),float(element.attrib['lon'])]
        except KeyError:
          pass
        for elet in element.iter('tag'):
          k = elet.attrib['k']
          v = elet.attrib['v']
          #one of the requirements
          if not re.search(problemchars,k):
            #looks like address?
            match=re.search(addpat,k)
            if match:
              #no additional sections, if do, ignore data
              if match.group(2) == None:
                #create address structure as needed
                if 'address' not in node.keys():
                  node['address']={}
                #stuff correct value into address structure
                node['address'][match.group(1)]=v
            #test name pattern?
            else:
              match=re.search(namepat,k)
              if match:
                #no additional sections, if do, ignore data
                if match.group(2) == None:
                  #create address structure as needed
                  if 'name' not in node.keys():
                    node['name']=[]
                  #append language to name array if not already
                  if not match.group(1) in node['name']:
                    node['name'].extend([match.group(1)])
              #all other values, this is not enumerated
              else:
                #the name does not fit into name:en pattern
                if k == 'name':
                  #default name stored
                  node['nameDef']=v
                  if 'name' not in node.keys():
                    node['name']=[]
                  #add to array
                  node['name'].extend(['default'])
                else:
                  node[k]=v
                #trying to catch all known tags
                if k not in nottags:
                  nottags[k]=1
        #take care of way's reference list
        if element.tag == "way":
          node['node_refs'] = []
          for nd in element.iter('nd'):
            node['node_refs'].append(nd.attrib['ref'])
        return node
    elif element.tag in ELETAGS:
        #pprint.pprint(element, out2)
        pass
    else:
        return None

def process_map(file_in, pretty = False):
    # You do not need to change this file
    file_out = "{0}.json".format(file_in)
    data = []
    with codecs.open(file_out, "w") as fo:
        for _, element in ET.iterparse(file_in):
            el = shape_element(element)
            if el:
                data.append(el)
                if pretty:
                    fo.write(json.dumps(el, indent=2)+"\n")
                else:
                    fo.write(json.dumps(el) + "\n")
    return data

if __name__ == "__main__":
    #data = process_map('mapDallas.osm', True)
    data = process_map('mapTaipei.osm', True)
    #out=open('mapPP.json', 'w')
    out1=open('mapnottags.txt', 'w')
    pprint.pprint(nottags, out1)
    #pprint.pprint(unicode(data), out)
