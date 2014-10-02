from django.shortcuts import render
import json
import os
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from app.models import *
from middleware.ngram import find_and_init_ngrams_for_property
from middleware.yelpspider import YelpSpider
from middleware.ner_lib import *
import urllib2
from BeautifulSoup import BeautifulSoup


# Create your views here.

class AppLandingView(View):

    def get(self, request):
        return render_to_response("app/ember_main.html", {}, context_instance=RequestContext(request))

    def post(self, request):
        val = URLValidator()
        url = request.POST["yelp_url"]
        if str(url).startswith("http://m."):
            url = url.replace("http://m.", "http://www.")
        if str(url).startswith("www."):
            url = url.replace("www.", "http://www.")
        if not str(url).startswith("http://www."):
            url = ''.join("http://www.", url)
        try:
            val(request.POST["yelp_url"])
        except ValidationError, e:
            return HttpResponse(json.dumps({"property_id": -1}), content_type="application/json")
        soup = BeautifulSoup(urllib2.urlopen(request.POST["yelp_url"]))
        if not "| Yelp" in soup.title.string:
            return HttpResponse(json.dumps({"property_id": -1}), content_type="application/json")
        propname = soup.title.string.replace("| Yelp", "")
        test_l = Property.objects.filter(name=propname)
        if len(test_l):
            prop = test_l[0]
        else:
            prop = Property(name=propname, yelp_url=request.POST["yelp_url"])
            prop.save()
        return HttpResponse(json.dumps({"property_id": prop.id}), content_type="application/json")

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(AppLandingView, self).dispatch(*args, **kwargs)


class PropertyMetasView(View):

    def get(self, request, property_id):
        """
        Returns ember-friendly dicts for property metadata
        """
        dict_list = []
        prop = Property.objects.get(id=property_id)
        dict_list.append(prop.get_property_meta_dict())

        return HttpResponse(json.dumps({"propertyMetas": dict_list}), content_type="application/json")


class PropertyMetaView(View):

    def get(self, request):
        """
        Returns ember-friendly dicts for property metadata
        """
        dict_list = []
        if len(Property.objects.all()) > 10:
            prop_list = Property.objects.order_by('-pk')[:10]
        else:
            prop_list = Property.objects.order_by('-pk')
        for prop in prop_list:
            dict_list.append(prop.get_property_meta_dict())

        return HttpResponse(json.dumps({"propertyMetas": dict_list}), content_type="application/json")


class PropertiesView(View):

    def get(self, request, property_id):
        """
        Returns ember-friendly dicts for a property and its associated reviews
        """
        # Grab property
        prop = Property.objects.get(id=property_id)

        # If there's no reviews yet (initial GET) grab 'em
        if len(prop.reviews.all()) == 0:
            review_date_cutoff = 2011
            yelp_spider = YelpSpider(url=prop.yelp_url, property_id=prop.id, provider_name="Yelp", review_date_cutoff=review_date_cutoff)
            # print "Starting Yelp spider for {0}".format(prop.name)
            yelp_spider.start()
            print "Yelp done!"

        # If there's no topics yet, build them (now using NOUNPHRASE).
        if len(prop.topics.all()) == 0:
            docs = []
            for r in prop.reviews.all():
                docs.append({"text": r.text, "id": r.id})
            noun_phrase_list = pos_tag_text_documents(docs)
            new_phrases = []
            # Bucket noun phrases with same subject together.
            for n in noun_phrase_list:
                if len(new_phrases):
                    found = False
                    for np in new_phrases:
                        if n["noun_phrase"].split(' ')[1] == np["noun_phrase"]:
                            found = True
                            for i in n["ids"]:
                                np["ids"].append(i)
                        if len(np["noun_phrase"].split(' ')) == 2 and n["noun_phrase"].split(' ')[1] == np["noun_phrase"].split(' ')[1]:
                            np["noun_phrase"] = n["noun_phrase"].split(' ')[1]
                            found = True
                            for i in n["ids"]:
                                np["ids"].append(i)
                    if not found:
                        new_phrases.append(n)
                else:
                    new_phrases.append(n)
            if len(new_phrases) > 10:
                new_phrases = new_phrases[:10]

            for n in new_phrases:
                if n["noun_phrase"] != "this place" and n["noun_phrase"] != "place" and n["noun_phrase"] != "this restaurant":
                    new_topic = Topic(name=n["noun_phrase"], category='NOUNPHRASE')
                    new_topic.save()
                    for rid in n["ids"]:
                        new_topic.reviews.add(Review.objects.get(id=rid))
                    new_topic.save()
                    prop.topics.add(new_topic)
                    prop.save()
    
        # Uncomment to use NGRAM topics instead
        # find_and_init_ngrams_for_property(prop)

        return HttpResponse(json.dumps({"properties": [prop.get_ember_dict()], "reviews": prop.get_all_review_dicts_for_ember(), "topics": prop.get_all_topic_dicts_for_ember()}), content_type="application/json")

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(PropertiesView, self).dispatch(*args, **kwargs)


class ReviewsView(View):

    def get(self, request, review_id):
        """
        Returns ember-friendly dicts for a review
        """
        
