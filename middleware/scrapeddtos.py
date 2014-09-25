# -*- coding: utf-8 -*-
from pattern.web import URL
import scrape
from scrape.models import Property

__author__ = "MDee"


class ScrapedTextProviderDTO(object):
    """
    """
    def __init__(self, name, url, rated=True, domains=[], max_rating=5.0):
        '''Create a provider.'''
        self.name = name
        self.url = url
        self.rated = rated
        self.max_rating = max_rating
        if domains:
            self.domains = domains
        else:
            base_url = URL(url)
            self.domains = [base_url.domain]


class ScrapedTextDTO(object):
    """
    """
    def __init__(self, property_id, provider, content, pub_date,
                 source_url=None, date_format="%Y-%m-%d", rating=None, title=None):
        # Each of these is raw, scraped data
        self.property_id = property_id
        self.provider = provider
        self.rating = rating
        self.content = content
        self.pub_date = pub_date
        self.title = title
        self.source_url = source_url
        self.date_format = date_format
        # Additionally, store the normalized rating
        try:
            self.normalized_rating = float(rating) / provider.max_rating
        except TypeError:
            print "Error trying to create normalized rating for TripAdvisor review"
            print "Rating value: {0}".format(rating)
            raise Exception

    def save(self, *args, **kwargs):
        """
        """
        property = Property.objects.get(pk=self.property_id)

    def __unicode__(self):
        return "\nDate: {0} Rating: {1}\nSource: {2}\n{3}".format(self.pub_date, self.rating, self.source_url, self.content)

    def __str__(self):
        return unicode(self).encode("utf-8")
