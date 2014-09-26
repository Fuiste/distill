from django.shortcuts import render
import json
import os
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from app.models import *
from middleware.ngram import find_and_init_ngrams_for_property
from middleware.yelpspider import YelpSpider
import urllib2
from BeautifulSoup import BeautifulSoup


# Create your views here.

class AppLandingView(View):

    def get(self, request):
        return render_to_response("app/ember_main.html", {}, context_instance=RequestContext(request))

    def post(self, request):
        # prop = Property.objects.get(name="Ian's Pizza on State (fake)")
        print request.POST["yelp_url"]
        soup = BeautifulSoup(urllib2.urlopen(request.POST["yelp_url"]))
        print soup.title.string
        prop = Property(name=soup.title.string, yelp_url=request.POST["yelp_url"])
        prop.save()
        return HttpResponse(json.dumps({"property_id": prop.id}), content_type="application/json")

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(AppLandingView, self).dispatch(*args, **kwargs)


class PropertiesView(View):

    def get(self, request, property_id):
        """
        Returns ember-friendly dicts for a property and its associated reviews
        """
        prop = Property.objects.get(id=property_id)
        # Force NGRAM topics for now
        # Uncomment for speedup, not it just runs all the time.
        #generate = True
        #if len(prop.topics.all()):
        #    if prop.topics.all().category == 'NGRAM':
        #        generate = False
        #if generate:
        #    find_and_init_ngrams_for_property(prop)
        #review_date_cutoff = 2011
        #yelp_spider = YelpSpider(url=prop.yelp_url, property_id=prop.id, provider_name="Yelp", review_date_cutoff=review_date_cutoff)
        #print "Starting Yelp spider for {0}".format(prop.name)
        #yelp_spider.start()
        #print "Yelp done!"
        #find_and_init_ngrams_for_property(prop)
        return HttpResponse(json.dumps({"properties": [prop.get_ember_dict()], "reviews": prop.get_all_review_dicts_for_ember(), "topics": prop.get_all_topic_dicts_for_ember()}), content_type="application/json")

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(PropertiesView, self).dispatch(*args, **kwargs)


class ReviewsView(View):

    def get(self, request, review_id):
        """
        Returns ember-friendly dicts for a review
        """
        
