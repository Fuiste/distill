# -*- coding: utf-8 -*-
import re
from nltk.parse.stanford import StanfordParser
import os
import threading
from middleware.text_format import replace_special_chars_in_text
import ner
from nltk.tree import *
import urllib
import urllib2
import json

threading._DummyThread._Thread__stop = lambda x: 42


__author__ = "fuiste"

middleware_dir = os.path.dirname(__file__)
parse_url = "http://distill-server.herokuapp.com/parse"


# Old noun phrase extraction method.
def extract_noun_phrases(pos_str):
    new_noun_phrase_regex = r"\(NP\s(?P<noun_phrase>(\([A-Z\$]+\s\w{4,}\)(\s)?)+)\)"
    pos_regex = r"(((\s)?\([A-Z\$]+)|(\)(\s)?))"
    noun_phrases = []
    matches = list(re.findall(new_noun_phrase_regex, pos_str))
    for m in matches:
        noun_phrase = re.sub(pos_regex, "", m[0]).strip()
        if len(noun_phrase.split(" ")) > 1:
            noun_phrases.append(noun_phrase)
    return noun_phrases


# Extract phrases from a parsed (chunked) tree
# Phrase = tag for the string phrase (sub-tree) to extract
# Returns: List of deep copies;  Recursive
# Use regex to remove opening and closing parentheses
def ExtractPhrases( myTree, phrase):
    myPhrases = []
    if (myTree.label() == phrase):
        myPhrases.append( myTree.copy(True) )
    for child in myTree:
        if (type(child) is Tree):
            list_of_phrases = ExtractPhrases(child, phrase)
            if (len(list_of_phrases) > 0):
                phrase_strings = []
                for ph in list_of_phrases:
                    np_strs = extract_noun_phrases(str(ph))
                    # phrase_strings.append(' '.join(ph.leaves()))
                    phrase_strings.extend(np_strs)
                myPhrases.extend(phrase_strings)
    return myPhrases


def pos_tag_text_documents(text_documents):
    formatted_text = []#replace_special_chars_in_text(text_documents=text_documents, lowercase=False)
    for doc in text_documents:
        sentences = re.split(r' *[\.\?!][\'"\)\]]* *', doc["text"])
        formatted_text.append({"sentences": sentences, "id": doc["id"]})
    # tagger = ner.SocketNER(host='http://distill-server.herokuapp.com', port=8080)
    doc_copy = []
    # maps noun phrases to their documents
    noun_phrase_map = {}
    formatted_cuts = []
    for t in formatted_text:
        if len(formatted_cuts):
            found = False
            for c in formatted_cuts:
                if len(c) < 4:
                    c.append(t)
                    found = True
            if not found:
                formatted_cuts.append([t])
        else:
            formatted_cuts.append([t])
    noun_phrases = []
    total_c = len(formatted_text)
    cur_c = 0
    for cut in formatted_cuts:
        request_object = urllib2.Request(parse_url, json.dumps(cut), {"Content-Type": "application/json"})
        response = urllib2.urlopen(request_object)
        html_arr = json.loads(response.read())
        cur_c = cur_c + len(cut)
        print "{0} / {1} reviews tagged".format(cur_c, total_c)
        noun_phrases.extend(html_arr)
    print "Tagging done, mapping phrases to topics"
    if noun_phrases:
        for p in noun_phrases:
            phrases = extract_noun_phrases(p["phrase"])
            for ph in phrases:
                if ph not in noun_phrase_map:
                    noun_phrase_map[ph] = set()
                noun_phrase_map[ph].add(p["id"])
    noun_phrase_list =[]
    for noun_phrase, id_set in noun_phrase_map.iteritems():
        noun_phrase_list.append({"noun_phrase": noun_phrase, "ids": list(id_set)})
    noun_phrase_list = sorted(noun_phrase_list, key=lambda n: len(n["ids"]), reverse=True)
    print "\nTop 10 noun phrases for this group:"
    for n in noun_phrase_list[:20]:
        print "\t" + n["noun_phrase"] + " - {0}".format(n["ids"])
    return noun_phrase_list

def get_ner_for_text_documents(text_documents):
    """Tags a list of strings for NER

    Arguments:
        text_documents: A list of strings
    """
    non_o_set = set()
    formatted_text = replace_special_chars_in_text(text_documents=text_documents, lowercase=False)
    joined_texts = " ".join(formatted_text)
    tagger = ner.SocketNER(host='localhost', port=8080)
    # print "Attempting to tag set with {0} documents".format(len(formatted_text))
    # print tagger.get_entities(joined_texts)
