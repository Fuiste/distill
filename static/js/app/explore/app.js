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

    Explore.ExploreIndexRoute = Em.Route.extend({
      actions: {
        submitUrl: function(){
          var self = this;
          var url = this.controllerFor('exploreIndex').get('yelpURL');
          $.ajax({
            url: '/explore',
            data: {yelp_url: url},
            type: 'POST'
          }).success(function(resp){
            self.transitionTo('processing', {queryParams: {property: resp["property_id"]}});
          });
        }
      }
    });

    Explore.ExploreIndexController = Em.Controller.extend({
      yelpURL: "",
      testVar: "HEY THERE",
      actions: {},
    });

    Explore.ProcessingRoute = Em.Route.extend({
      model: function(){},
      setupController: function(controller, model){
        var self = this;
        var propertyPromise = self.store.find('property', controller.get('property'));
        propertyPromise.then(function(prop){
          self.transitionTo('property.index', prop);
        });
      }
    });

    Explore.ProcessingController = Em.Controller.extend({
      queryParams: ['property'],
      dataset: null
    });

    Explore.PropertyIndexRoute = Em.Route.extend({});

    Explore.PropertyIndexController = Em.Controller.extend({});

  });
}(window.jQuery, window.Handlebars, window.Ember, window.d3, window.vg);
