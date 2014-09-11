from django.db import models

# Create your models here.


class Property(models.Model):
    """
    A physical location belonging to a Customer organization
    """
    #  Instance fields
    name = models.CharField(max_length=100, db_column="name")
    yelp_url = models.URLField(null=True, blank=True,
                               help_text="The URL for this property's reviews on Yelp, if it exists")
    facebook_url = models.URLField(null=True, blank=True, default="",
                                   help_text="The URL to the property's facebook page")
    google_reviews_url = models.URLField(null=True, blank=True, default="",
                                         help_text="The URL for this property's reviews on Google+, if it exists")
    tripadvisor_url = models.URLField(null=True, blank=True, default="",
                                      help_text="The URL for this property's reviews on TripAdvisor, if it exists")
    urbanspoon_url = models.URLField(null=True, blank=True, default="")
    yelp_biz_id = models.CharField(null=True, blank=True, default="", max_length=200, help_text="This is the ID for the business on Yelp, if it exists")
    # Provider Metas
    yelp_provider_meta = models.ForeignKey(ProviderMeta, null=True, blank=True, on_delete=models.SET_NULL, related_name="yelp_provider_meta")
    tripadvisor_provider_meta = models.ForeignKey(ProviderMeta, null=True, blank=True, on_delete=models.SET_NULL, related_name="tripadvisor_provider_meta")
    google_reviews_provider_meta = models.ForeignKey(ProviderMeta, null=True, blank=True, on_delete=models.SET_NULL, related_name="google_reviews_provider_meta")
    urbanspoon_provider_meta = models.ForeignKey(UrbanspoonProviderMeta, null=True, blank=True, on_delete=models.SET_NULL, related_name="urbanspoon_provider_meta")


class ProviderMeta(SoftDeletionModel):
    name = models.CharField(max_length=100)
    url = models.URLField(null=True, blank=True)
    public_id = models.CharField(max_length=500, null=True, blank=True)


class UrbanspoonProviderMeta(ProviderMeta):
    city_id = models.IntegerField(null=True, blank=True)


class ScrapedTextProvider(SoftDeletionModel):
    name = models.CharField(max_length=50, help_text="The name of the website")
    url = models.URLField(null=True, blank=True)
    rated = models.BooleanField(default=True, help_text="Whether or not this site lets users provide explicit ratings")
    max_rating = models.FloatField(default=5.0, null=True, blank=True)
    unit = models.CharField(max_length="30", default="star", help_text="Basic unit for a rating. Defaults to 'stars'.")


class ScrapedText(models.Model):
    property = models.ForeignKey(Property, null=True, blank=True, db_column="property_id")
    provider = models.ForeignKey(ScrapedTextProvider, null=True, blank=True, db_column="provider_id")
    content = models.TextField(max_length=9999, help_text="The full text of the review.")
    title = models.CharField(max_length=200, null=True, blank=True, default="",
                             help_text="Some reviews have a title given by the user")
    html_content = models.TextField(max_length=9999, default="", null=True, blank=True,
                                    help_text="The full text of the review, with HTML annotations for the client")
    source_url = models.URLField(null=True, blank=True)
    pub_date = models.DateField(default=datetime.today().date(), null=True, blank=True,
                                help_text="When the original review was published.")
    rating = models.FloatField(default=-1, null=True, blank=True, help_text="The unnormalized rating, if it exists")
    textributes = PickledObjectField(help_text="The set of Textributes for this ScrapedText instance")
    sentences = PickledObjectField(help_text="The set of sentences in this ScrapedText")
    human_set_textributes = PickledObjectField(null=True, blank=True, default=[],
                                               help_text="The set of Textributes set by a person for this ScrapedText instance")
    unique_attr = models.CharField(max_length=200, default="content")

    DEFAULT_DATE_FORMAT = "%Y-%m-%d"
