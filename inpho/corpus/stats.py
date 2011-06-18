#loadCorpus

# Iterate through corpus dir and find all sep_dirs and index files
# Alternatively, iterate through sep_dirs of SQL

# Open HTML file and grab sentence list
# 
# title.replaceAll(" \\(stanford encyclopedia of philosophy\\)", "");                 
# title.replaceAll("sep: ", "");   

# documentString which is just sentenceList.join()

# appearList is set of all terms which appear in the sentence
# occurList is set of all terms occuring in the document

import logging
import re
import string
import subprocess
from collections import defaultdict

# http://nltk.googlecode.com/svn/trunk/doc/api/nltk.tokenize.punkt.PunktSentenceTokenizer-class.html
from nltk.tokenize import PunktSentenceTokenizer as Tokenizer

def get_document_occurrences(document, terms, doc_terms=[]):
    """
    Returns a list of terms occuring in the document. 
    Semantically equivalent to [term for term in terms if term in document]
    """

    occurrences = []
    
    # iterate over terms to be scanned
    for term in terms:
        if term not in doc_terms:
            # build list of search patterns starting with label
            pattern = ['\b%s\b' % term.label]
            pattern.extend(term.searchpatterns)
            for pattern in term.searchpatterns:
                try:
                    if re.search(pattern, document, flags=re.IGNORECASE):
                        occurrences.append(term)
                        break
                except re.error:
                    logging.warning('Term %d (%s) pattern "%s" failed' % 
                                    (term.ID, term.label, pattern))

    if doc_terms:
        occurrences.extend(doc_terms)

    return occurrences

def get_sentence_occurrences(document, terms, doc_terms=[], 
                             remove_overlap=False):
    """
    Returns a list of lists representing the terms occuring in each sentence.
    Semantically equivalent to: 
    [[term for term in terms if term in sent] for sent in document]
    """
    terms_present = set(get_document_occurrences(document, terms, doc_terms))

    # Use a Tokenizer from NLTK to build a sentence list
    tokenizer = Tokenizer(document)
    sentences = tokenizer.tokenize(document)
    
    # Create a list of lists containing the collection of terms which cooccurr
    # in a sentence
    occurrences = []
    for sentence in sentences:
        sentence_occurrences = [] 

        for term in terms_present:
            if term not in doc_terms:
                # build list of search patterns starting with label
                pattern = ['\b%s\b' % term.label]
                pattern.extend(term.searchpatterns)

                for pattern in term.searchpatterns:
                    try:
                        # search for any occurrence of term, stop when found
                        if re.search(pattern, document, flags=re.IGNORECASE):
                            occurrences.append(term)
                            break
                    except re.error:
                        logging.warning('Term %d (%s) pattern "%s" failed' % 
                                        (term.ID, term.label, pattern))

        # remove overlapping elements
        if remove_overlap:
            to_remove = set()
            
            # build set of terms to remove
            for inside in sentence_occurrences:
                for term in sentence_occurrences:
                    if term != inside and\
                        inside.label.find(term.label) != -1:
                        to_remove.add(term)

            # remove terms
            for term in to_remove:
                sentence_occurrences.remove(term)

        # add to list of sentences if any terms are found
        if sentence_occurrences:
            if doc_terms:
                sentence_occurrences.extend(doc_terms)

            occurrences.append(sentence_occurrences)
    
    return occurrences

def prepare_apriori_input(document, terms, doc_terms=None, add_newline=True): 
    occurrences = get_document_occurrences(document, terms, doc_terms)
    sentence_occurrences = get_sentence_occurrences(document, terms, doc_terms)

    lines = []
    lines.append(string.join([str(term.ID) for term in occurrences]))
    for sent_occur in sentence_occurrences:
        lines.append(string.join([str(term.ID) for term in sent_occur]))

    if add_newline:
        lines = [line + '\n' for line in lines]

    return lines

def apriori(input_filename='output.txt', output_filename='edges.txt'):
    args = ['apriori', input_filename, output_filename,
            '0.00000000000000001', '0.00000000000000001']
    return subprocess.call(args)


def process_edges(occurrences_filename='output.txt', edges_filename='edges.txt'):
    # process occurrence and cooccurrence data
    occurrences = defaultdict(lambda: defaultdict(int))
    with open(occurrences_filename) as f:
        for line in f:
            ids = line.split()

            for ante in ids:
                for cons in ids:
                    occurrences[ante][cons] += 1

    edges = defaultdict(dict)
    with open(edges_filename) as f:
        for line in f:
            ante,cons,confidence,jweight = line.split()
            edges[(ante,cons)] = {'confidence':float(confidence), 
                                  'jweight':float(jweight),
                                  'occurrences':occurrences[ante][cons]}
    return edges

from math import log
def calculate_node_entropy(edges):
    probabilities = defaultdict(lambda: defaultdict(float))
    for edge,properties in edges.iteritems():
        ante,cons = edge
        probabilities[ante][cons] = properties['confidence']
    
    ents = defaultdict(float)
    for ante,conses in probabilities.iteritems():
        total_prob = sum(conses.values())
        normalized_probs = [x / total_prob for x in conses.values()]

        Hx = sum([x * (log(x) / log(2)) for x in normalized_probs])

        ents[ante] = -Hx

    return ents

def calculate_edge_weight(edges, ents):
    weights = defaultdict(float)
    if ents:
        max_entropy = max(ents.values())
        for edge, properties in edges.iteritems():
            ante,cons = edge
            entropy_diff = ents[ante] - ents[cons]
            entropy_norm = entropy_diff / max_entropy
            properties['weight'] = properties['jweight'] * entropy_norm
    else:
        print "ERROR PROCESSING EDGES. NO ENTROPY VALUES."

    return edges    
