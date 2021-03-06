from inpho.lib import rdf
from httplib import HTTPException
import logging
import os.path
import time
from urllib import quote_plus
from urllib2 import Request, urlopen, URLError, HTTPError

import inpho.helpers
from inpho.model.entity import Entity

from sqlalchemy.ext.associationproxy import association_proxy

class Journal(Entity):
    """
    Simple Journal class, has custom definitions for representation strings.
    """
    def __init__(self, name, **kwargs):
        self.label = name
        self.name = name
        for k, v in kwargs.iteritems():
            self.__setattr__(k, v)

    def __repr__(self):
        return '<Journal %d: %s>' % (self.ID, self.label.encode('utf-8'))

    def __str__(self):
        return self.label
    
    def url(self, filetype=None, action=None, id2=None):
        return inpho.helpers.url(controller="journal", id=self.ID, id2=id2,
                                 action=action, filetype=filetype)
    # Triple Generation Code
    def rdf(self, graph):
        graph.add((rdf.inpho['journal'], rdf.rdf['type'], rdf.foaf['person']))
        graph.add((rdf.inpho['journal'], rdf.rdfs['subClassOf'], rdf.inpho['entity']))
        
        graph.add((rdf.t['t' + str(self.ID)], rdf.rdf['type'], rdf.inpho['journal']))
        graph.add((rdf.t['t' + str(self.ID)], rdf.foaf['name'], rdf.Literal(self.label)))
        graph.add((rdf.t['t' + str(self.ID)], rdf.owl['sameAs'], rdf.e['e' + str(self.ID)]))
        
        return graph

    # Make graph of Triples
    def graph(self, graph=None):
        if graph == None:
            graph = rdf.make_graph()

        graph = self.rdf(graph)

        return graph


    abbrs = association_proxy('abbreviations', 'value')
    queries = association_proxy('query', 'value')

    def check_url(self):
        """ Verifies the journal still has a good URL. """
        # if journal does not have a URL, return None which is False-y
        if not self.URL:
            return None

        # attempt to open the URL, capture exceptions as failure
        try:
            request = Request(self.URL,
                headers={'User-Agent' : 
                ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:2.0.1)"
                 "Gecko/20100101 Firefox/4.0.1")})
            response = urlopen(request, timeout=15)
        except (URLError, HTTPError, IOError, HTTPException) as e:
            logging.warning("URL failed w/exception! [%s] %s" % (self.URL, e))
            return False

        self.last_accessed = time.time()

        # If there is a redirect, fix the url
        if self.URL != response.geturl():
            self.URL = response.geturl()

        return True

    @property
    def last_accessed_str(self, format="%x %X %Z"):
        return time.strftime(format, time.gmtime(self.last_accessed))

    @property
    def ISSN_google_url(self):
        google = "http://www.google.com/search?q="
        google += quote_plus("%s %s" % (self.label.encode("utf-8"), self.ISSN))
        return google 

    def json_struct(self, sep_filter=True, limit=10, extended=True):
        struct = { 'ID' : self.ID, 
                  'type' : 'journal',
                  'label' : self.label,
                  'sep_dir' : self.sep_dir,
                  'url' : self.url()}
        if extended:
            struct.update({
                  'website' : self.URL,
                  'language' : self.language,
                  'abbrs' : self.abbrs,
                  'queries' : self.queries,
                  'openAccess' : self.openAccess,
                  'active' : self.active,
                  'student' : self.student,
                  'ISSN' : self.ISSN })
        return struct

class Abbr(object):
    def __init__(self, value):
        self.value = value

class SearchQuery(object):
    def __init__(self, value):
        self.value = value
