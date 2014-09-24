# -*- coding: utf-8 -*-
import json
import re
import string
import math
from django.core.exceptions import ObjectDoesNotExist
from gensim import corpora, models, similarities
import logging
from nltk.util import ngrams
from app.models import *
import nltk


ENGLISH_STOP_WORDS = frozenset([
    "a", "about", "above", "across", "after", "afterwards", "again", "against",
    "all", "almost", "alone", "along", "already", "also", "although", "always",
    "am", "among", "amongst", "amoungst", "amount", "an", "and", "another",
    "any", "anyhow", "anyone", "anything", "anyway", "anywhere", "are",
    "around", "as", "at", "back", "be", "became", "because", "become",
    "becomes", "becoming", "been", "before", "beforehand", "behind", "being",
    "below", "beside", "besides", "between", "beyond", "bill", "both",
    "bottom", "but", "by", "call", "can", "cannot", "cant", "co", "con",
    "could", "couldnt", "cry", "de", "describe", "detail", "do", "done",
    "down", "due", "during", "each", "eg", "eight", "either", "eleven", "else",
    "elsewhere", "empty", "enough", "etc", "even", "ever", "every", "everyone",
    "everything", "everywhere", "except", "few", "fifteen", "fify", "fill",
    "find", "fire", "first", "five", "for", "former", "formerly", "forty",
    "found", "four", "from", "front", "full", "further", "get", "give", "go",
    "had", "has", "hasnt", "have", "he", "hence", "her", "here", "hereafter",
    "hereby", "herein", "hereupon", "hers", "herself", "him", "himself", "his",
    "how", "however", "hundred", "i", "ie", "if", "in", "inc", "indeed",
    "interest", "into", "is", "it", "its", "itself", "keep", "last", "latter",
    "latterly", "least", "less", "ltd", "made", "many", "may", "me",
    "meanwhile", "might", "mill", "mine", "more", "moreover", "most", "mostly",
    "move", "much", "must", "my", "myself", "name", "namely", "neither",
    "never", "nevertheless", "next", "nine", "no", "nobody", "none", "noone",
    "nor", "not", "nothing", "now", "nowhere", "of", "off", "often", "on",
    "once", "one", "only", "onto", "or", "other", "others", "otherwise", "our",
    "ours", "ourselves", "out", "over", "own", "part", "per", "perhaps",
    "please", "put", "rather", "re", "same", "see", "seem", "seemed",
    "seeming", "seems", "serious", "several", "she", "should", "show", "side",
    "since", "sincere", "six", "sixty", "so", "some", "somehow", "someone",
    "something", "sometime", "sometimes", "somewhere", "still", "such",
    "system", "take", "ten", "than", "that", "the", "their", "them",
    "themselves", "then", "thence", "there", "thereafter", "thereby",
    "therefore", "therein", "thereupon", "these", "they", "thick", "thin",
    "third", "this", "those", "though", "three", "through", "throughout",
    "thru", "thus", "to", "together", "too", "top", "toward", "towards",
    "twelve", "twenty", "two", "un", "under", "until", "up", "upon", "us",
    "very", "via", "was", "we", "well", "were", "what", "whatever", "when",
    "whence", "whenever", "where", "whereafter", "whereas", "whereby",
    "wherein", "whereupon", "wherever", "whether", "which", "while", "whither",
    "who", "whoever", "whole", "whom", "whose", "why", "will", "with",
    "within", "without", "would", "yet", "you", "your", "yours", "yourself",
    "yourselves", "I"])


def find_and_init_ngrams_for_property(prop, n=2):
    """
    Assuming all reviews are grabbed for a property, analyzes review space and builds topic models for ngrams of the given size
    
    Args:
        prop: a property model to analyze
        n: n-gram size
    Returns:
        True
    """
    if len(prop.topics.all()):
        print "Found stale topics, deleting..."
        prop.topics.all().delete()
    resps = ""
    # Grab all reivews for the property as one long string, then split them into n-grams
    for r in prop.reviews.all():
        resps += r.text
    words = [word.strip() for word in resps.split() if word not in ENGLISH_STOP_WORDS]
    grams = ngrams(words, n)

    # Find up to 5 most-common n-grams
    dist = nltk.FreqDist(grams)
    most_common = []
    if len(dist.items()) > 4:
        most_common = dist.items()[:5]
    else:
        most_common = dist.items()

    # create new n-gram topics
    ngz = []
    for gram in most_common:
        ngz.append(Topic(category='NGRAM', name=' '.join(gram[0])))
    for gram in ngz:
        gram.save()
        prop.topics.add(gram)
  
    # Map nodes to new Ngram models
    node_ngram_map = {}
    for r in prop.reviews.all():
        for i, ng in enumerate(ngz):
            if most_common[i][0] in ngrams([word.strip() for word in r.text.split() if word not in ENGLISH_STOP_WORDS], n):
                print "FOUND ONE"
                ng.reviews.add(r)
                ng.save()
    for ng in ngz:
        if len(ng.reviews.all()) < 2:
            ng.delete()
    return True

                
            





