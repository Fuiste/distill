# -*- coding: utf-8 -*-
import re
from nltk.parse.stanford import StanfordParser
import os
import threading
from middleware.text_format import replace_special_chars_in_text
import ner
from nltk.tree import *

threading._DummyThread._Thread__stop = lambda x: 42


__author__ = "MDee"

middleware_dir = os.path.dirname(__file__)
st = StanfordParser(middleware_dir + "/stanford_parser/stanford-parser.jar", middleware_dir + "/stanford_parser/stanford-models.jar")


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
    print middleware_dir + "/stanford_parser/stanford-parser.jar"
    formatted_text = []#replace_special_chars_in_text(text_documents=text_documents, lowercase=False)
    for doc in text_documents:
        sentences = re.split(r' *[\.\?!][\'"\)\]]* *', doc["text"])
        for s in sentences:
            formatted_text.append({"text": s.lower(), "review_id": doc["id"]})
    # tagger = ner.SocketNER(host='http://distill-server.herokuapp.com', port=8080)
    doc_copy = []
    # maps noun phrases to their documents
    noun_phrase_map = {}
    for index, td in enumerate(formatted_text):
        pos_str = st.raw_parse(td["text"])
        if pos_str:
            noun_phrases = ExtractPhrases(pos_str[0], 'NP')
        if noun_phrases:
            for p in noun_phrases:
                if p not in noun_phrase_map:
                    noun_phrase_map[p] = set()
                noun_phrase_map[p].add(td["review_id"])
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
