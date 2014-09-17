!function ($, _H, Em, d3, vg) {
  $(function(){

    window.Explore = Em.Application.create({
      LOG_TRANSITIONS: true,
      ENABLE_ALL_FEATURES: true,
      LOG_ACTIVE_GENERATION: true,
      LOG_VIEW_LOOKUPS: true
    });

    window.Explore.store = DS.Store.extend({
      adapter: DS.RESTAdapter
    });

    Explore.ResetScroll = Ember.Mixin.create({
      activate: function() {
        this._super();
        $('html,body').animate({
          scrollTop: 0
        }, 1000);
      }
    });

    Explore.Router.map(function() {
      this.resource('explore', {path: '/'}, function(){
      });
      this.resource('processing');
      this.resource('properties', {path: 'properties'}, function(){
      });
      this.resource('property', {path: 'property/:property_id'}, function(){
        this.resource('reviews', {path: '/reviews'}, function(){
        });
        this.resource('review', {path: '/review/:review_id'}, function(){
        });
      });
    });

    Explore.exploreIndexRoute = Em.Route.extend({
      yelpURL: "",
      renderTemplate: function(){
      },
      actions: {
        uploadComplete: function(datasetId){
          this.transitionTo('processing', {queryParams: {property: propertyId}});
        }
      }
    });

  });
}(window.jQuery, window.Handlebars, window.Ember, window.d3, window.vg);
