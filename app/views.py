from django.shortcuts import render
import json
import os
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

# Create your views here.

class AppLandingView(View):

    def get(self, request):
        return render_to_response("app/ember_main.html", {}, context_instance=RequestContext(request))

    def post(self, request):
        return HttpResponse(json.dumps({"property_id": 1}), content_type="application/json")

class PropertiesView(View):

    def get(self, request, property_id):
        """Returns dummy data for now
        """
        prop = {"name": "Test restaurant", "id": 1, "reviews": [1, 2, 3, 4, 5]}
        reviews = []
        reviews.append({"text": "This was an awesome place to eat.  The burgers were incredible", "id": 1, "grade": 5})
        reviews.append({"text": "It was mostly average.  The service was pretty slow.", "id": 2, "grade": 3})
        reviews.append({"text": "Absolutely unacceptable.  The waiter took 2 HOURS to bring our food.  Will not return.", "id": 3, "grade": 1})
        reviews.append({"text": "Very uninteresting American cuisine.  I may return, but it's not high on my list.", "id": 4, "grade": 3})
        reviews.append({"text": "I liked the food here.  Variety leaves a bit to be desired, but when you do a simple thing well, what need is there to change?", "id": 5, "grade": 4})
        return HttpResponse(json.dumps({"properties": [prop], "reviews": reviews}), content_type="application/json")
