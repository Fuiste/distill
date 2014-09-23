# -*- coding: utf-8 -*-
import json
import re
import string
import math
from django.core.exceptions import ObjectDoesNotExist
from gensim import corpora, models, similarities
import logging
from app.models import Tree, Node, Prompt, Response, Ngram
from nltk.util import ngrams
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
    "yourselves"])


def get_all_nodes_in_tree(root_node):
    """Recursive. Using a breadth-first traversal, finds all nodes in the tree rooted by root_node

    Args: 
        root_node: A node model representing the root from where to begin
    Returns:
        An string of response texts within the tree bound by root_node
    """
    nodes = [root_node]
    queue = list(root_node.children.all())
    while len(queue):
        node = queue.pop(0)
        nodes.append(node)
        queue.extend(list(node.children.all()))
    return nodes


def find_most_common_ngrams(root_node, n=2):
    """Search the tree rooted by root_node for the most common n-grams

    Args: 
        root_node: a Node model from which to begin the search
        n: n-gram size (2=bigram, 3=trigram, etc...)
    Returns:
        An array of dicts representing up to 5 n-grams in the form:
          [{"value": <STRING>, "count": <INT>}, {"value": <STRING>, "count": <INT>}, ...]
    """
    nodes = get_all_nodes_in_tree(root_node)
    # Grab all responses in the tree as one long string, then split them into n-grams
    resps = ""
    for node in nodes:
        resps += node.response
        if len(node.ngrams.all()):
            node.ngrams.all().delete()
    words = [word.strip() for word in resps.split() if word not in ENGLISH_STOP_WORDS]
    grams = ngrams(words, n)

    # Find up to 5 most-common n-grams
    dist = nltk.FreqDist(grams)
    most_common = []
    if len(dist.items()) > 4:
        most_common = dist.items()[:5]
    else:
        most_common = dist.items()

    # create new n-grams
    try:
        ngram_id_gen = Ngram.objects.latest("id").id
    except ObjectDoesNotExist as ng:
        ngram_id_gen = -1
    ngz = []
    for gram in most_common:
        ngram_id_gen += 1
        ngz.append(Ngram(id=ngram_id_gen, text=' '.join(gram[0])))
    Ngram.objects.bulk_create(ngz)
    for gram in ngz:
        gram.save()
  
    # Map nodes to new Ngram models
    node_ngram_map = {}
    for node in nodes:
        ngram_indices = []
        for i, ng in enumerate(ngz):
            if most_common[i][0] in ngrams([word.strip() for word in node.response.split() if word not in ENGLISH_STOP_WORDS], n):
                ngram_indices.append(i)
                print ng.text
        node.ngrams.add(*[ngz[k] for k in ngram_indices])
    for node in nodes:
        print node.ngrams.all()

    """
    print most_common
    for gram in most_common:
        for node in nodes:
            resp = [word.strip() for word in node.response.split() if word not in ENGLISH_STOP_WORDS]
            resp_grams = ngrams(resp, n)
            if gram[0] in resp_grams:
                tgt_gram = Ngram.objects.filter(text=' '.join(gram[0]))
                new_gram = None
                if len(tgt_gram):
                    new_gram = tgt_gram[0]
                else:
                    new_gram = Ngram(text=' '.join(gram[0]))
                    new_gram.save()
                node.ngrams.add(new_gram)
    """
                
            





