# -*- coding: utf-8 -*-
import re
from nltk.tag.stanford import NERTagger
import os
import threading
from middleware.text_format import replace_special_chars_in_text
import ner

threading._DummyThread._Thread__stop = lambda x: 42


__author__ = "MDee"

middleware_dir = os.path.dirname(__file__)
st = NERTagger(middleware_dir + "/stanford_ner_files/english.all.3class.distsim.crf.ser.gz",
               middleware_dir + "/stanford_ner_files/stanford-ner.jar")


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


def pos_tag_text_documents(text_documents):
    formatted_text = text_documents#replace_special_chars_in_text(text_documents=text_documents, lowercase=False)
    tagger = ner.SocketNER(host='localhost', port=4466)
    doc_copy = []
    # maps noun phrases to their documents
    noun_phrase_map = {}
    for index, td in enumerate(formatted_text):
        pos_str = tagger.tag_text("parse " + td)
        noun_phrases = extract_noun_phrases(pos_str)
        if noun_phrases:
            for p in noun_phrases:
                if p not in noun_phrase_map:
                    noun_phrase_map[p] = set()
                noun_phrase_map[p].add(index)
    noun_phrase_list =[]
    for noun_phrase, id_set in noun_phrase_map.iteritems():
        noun_phrase_list.append({"noun_phrase": noun_phrase, "ids": list(id_set)})
    noun_phrase_list = sorted(noun_phrase_list, key=lambda n: len(n["ids"]), reverse=True)
    print "\nTop 10 noun phrases for this group:"
    for n in noun_phrase_list[:20]:
        print "\t" + n["noun_phrase"] + " - {0}".format(len(n["ids"]))
    return None

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
