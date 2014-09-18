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
        reviews.append({"text": "This place is amazing - the food, service, atmosphere, everything is done well.  They've such carefully crafted and complex tasting pizzas.  They've high quality ingredients, the pizzas served hot, and even their salads are good.  Their staff is always friendly, greets you at the door, and certainly knows their pizza.  I love their wall art, too I'm a well known carnivore and I crave these guys' salad pizza with artichokes, olives, tomatoes, and salad (don't get me wrong, I still get a smokey bandit or BBQ tot...but I rave about a salad pizza to my friends and they're stunned to hear me endorse something vegetarian).  Definitely one of the places I'll miss the most moving away :(", "id": 1, "grade": 5})
        reviews.append({"text": "Ever since my early visits in Madison I wanted to try Ian's.  Somehow we always ran out of time doing family stuff, but this time we got to pick up some pizzas...  Mac and Cheese, Florentine and Steak with barbecue sauce were really great  I was not hugely in on the crust, although it is ok, but I very much like the flavors on the toppings and the staff were great!!  I look forward to trying more pizza as my grandson is going to be born this week and if he has our family taste for pizza, we must continue the tradition....", "id": 2, "grade": 3})
        reviews.append({"text": "Not sure what all the hoopla is about this pizza, it all tastes bland to me. Doesn't matter if you get the mac and cheese pie or a roasted red pepper and feta pie, the crust is so bland and the sauce/cheese lacks any flavor at all.Salad bar is 5 stars btw", "id": 3, "grade": 2})
        reviews.append({"text": "I'd say Ian's is recognized more for their unconventional pizza ideas than the actual quality of the pizza. I got the mac and cheese pizza which was pretty much, um.. mac and cheese.. on pizza (try not to envy my way with words). I actually expected it to be a little cheesier though, but it was pretty flat. There was a burrito pizza that I was almost tempted to try, had I not glanced a tiny hair on one of the slices.  In my opinion, definitely worth a try but nothing to write home about.", "id": 4, "grade": 3})
        reviews.append({"text": "I've had good and meh experiences here.  The service is always friendly, but often seem kind of frazzled.  I don't get the mac and cheese pizza at ALL. I think it's super bland. Their vegetarian options are also usually a little one note -- some sort of blend of tomato/pesto/cheese flavor. I'd love more veggie-heavy but interesting dishes.  The main thing I've come to like is the Southwest Salad. I started an internship on the square so on Tuesdays I head in .. and nearly every week they've been out of something for the salad! I got it as a whole ONCE in the past 5 weeks or so. I told my co-worker how yummy it was, she went to try it out, they were out of everything, and she got another salad ... and hated it. Haha. Come on!", "id": 5, "grade": 4})
        return HttpResponse(json.dumps({"properties": [prop], "reviews": reviews}), content_type="application/json")
