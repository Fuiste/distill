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
from middleware.rq_lib import *
import urllib2
from BeautifulSoup import BeautifulSoup
import django_rq


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


class PropertyStatusView(View):

    def get(self, request, property_id):
        """
        Returns ember-friendly dicts for a property's status
        """
        # Grab property
        prop = Property.objects.get(id=property_id)

        # If there's no reviews yet (initial GET) grab 'em
        if prop.yelp_scraped == False:
            if not prop.yelp_processing:
                prop.reviews.all().delete()
                django_rq.enqueue(scrape_yelp_for_reviews, prop.id)

        if prop.yelp_scraped == True and prop.topics_analyzed == False:
            if not prop.topics_processing:
                prop.topics.all().delete()
                django_rq.enqueue(analyze_reviews_for_topics, prop.id)

        return HttpResponse(json.dumps({"propertyStatuses": [prop.get_property_status_dict()]}), content_type="application/json")

        # return HttpResponse(json.dumps({"properties": [prop.get_ember_dict()], "reviews": prop.get_all_review_dicts_for_ember(), "topics": prop.get_all_topic_dicts_for_ember()}), content_type="application/json")

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(PropertyStatusView, self).dispatch(*args, **kwargs)


class PropertiesView(View):

    def get(self, request, property_id):
        """
        Returns ember-friendly dicts for a property, AFTER scraping and analysis has been done
        """
        # Grab property
        prop = Property.objects.get(id=property_id)
    
        return HttpResponse(json.dumps({"properties": [prop.get_ember_dict()], "reviews": prop.get_all_review_dicts_for_ember(), "topics": prop.get_all_topic_dicts_for_ember()}), content_type="application/json")

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(PropertiesView, self).dispatch(*args, **kwargs)


