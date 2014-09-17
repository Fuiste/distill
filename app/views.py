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
