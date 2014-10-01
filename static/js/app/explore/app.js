!function ($, _H, Em, d3, vg) {

  $('#ratings-affix').affix({
    offset: {
      top: 100
    , bottom: function () {
        return (this.bottom = $('.footer').outerHeight(true))
      }
    }
  })

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
          var url = this.controllerFor('exploreIndex').get('yelpUrl');
          self.controllerFor('exploreIndex').set('checking', true);
          $.ajax({
            url: '/explore',
            data: {yelp_url: url},
            type: 'POST'
          }).success(function(resp){
            self.controllerFor('exploreIndex').set('checking', false);
            if(resp["property_id"]==-1){
              self.controllerFor('exploreIndex').set('badUrl', true);
              self.controllerFor('exploreIndex').set('yelpUrl', "");
            }else{
              self.controllerFor('exploreIndex').set('badUrl', false);
              self.transitionTo('processing', {queryParams: {property: resp["property_id"]}});
            }
          });
        },
        loadProperty: function(property){
          this.controllerFor('exploreIndex').set('badUrl', false);
          this.controllerFor('exploreIndex').set('checking', false);
          this.transitionTo('processing', {queryParams: {property: property.get('id')}});
        }
      }
    });

    Explore.ExploreIndexController = Em.Controller.extend({
      yelpUrl: "",
      checking: false,
      badUrl: false,
      properties: function(){
        return this.store.findAll('propertyMeta');
      }.property(),
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

    Explore.PropertyIndexRoute = Em.Route.extend({
      actions: {
        selectTopic: function(topic, property){
          var x = topic.get('selected');
          topic.set('selected', !x);
          property.set('allSelected', false);
        },
        anyAll: function(property){
          var x = property.get('anyFilter');
          property.set('anyFilter', !x);
        },
        selectAllTopics: function(property){
          if(!property.get('allSelected')){
            property.get('topics').forEach(function(t){
              t.set('selected', false);
            });
            property.set('allSelected', true);
          }else{property.set('allSelected', false);}
        }
      }
    });

    Explore.PropertyIndexController = Em.Controller.extend({
    });

    Explore.VerticalBarChartComponent = Ember.Component.extend({
      classNames: ['animated', 'fadeInDown'],
      didInsertElement: function(){
        Ember.run.once(this, 'update');
      },
      updateContent: function(){
        Ember.run.once(this, 'update');
      }.observes('distributions'),
      update: function(){
        var self = this;
        var groups = this.get('data');
        var groupData = []
        groups.forEach(function(g){
          var xAxisLabel = g.score;
          var color = '#e09e26';
          groupData.push({x: xAxisLabel, y: g.num, color: color});
        });
        var padding = {top: 10, left: 50, bottom: 70, right: 10};
        var spec = {
          padding: padding,
          width: self.$().width() - padding.left - padding.right,
          height: 300,
          data: [{name : 'Scores', values: groupData}],
          scales: [
            {name: 'x', type: 'ordinal', range: 'width', domain: {data: 'Scores', field: 'data.x'}},
            {name: 'y', range: 'height', nice:true, domain: {data: 'Scores', field: 'data.y'}}
          ],
          axes: [
            {type: 'x', scale: 'x', title: "Score", properties: {title: {dy: {value: 20}, fontSize: {value: 16}, fill: {value: '#fff'}}, labels: {angle: {value: -50}, dx: {value: -20}, fill: {value: '#fff'}}, ticks: {stroke: {value: '#fff'}}, axis: {stroke: {value: '#fff'}}}},
            {type: 'y', scale: 'y', title: "# of Reviews", properties: {title: {fontSize: {value: 16}, fill: {value: '#fff'}}, labels: {fill: {value: '#fff'}}, ticks: {stroke: {value: '#fff'}}, axis: {stroke: {value: '#fff'}}}}
          ],
          marks: [
            {
              type: 'rect',
              from: {data: 'Scores'},
              properties: {
                enter: {
                  x: {scale: 'x', field: 'data.x'},
                  width: {scale: 'x', band:true, offset:-1},
                  y: {scale: 'y', field: 'data.y'},
                  y2: {scale: 'y', value:0}
                },
                update: { fill: {field: 'data.color'}, stroke: {value: '#fff'}, strokeWidth: {value: '0.5'}}//,
//                hover: { fill: {value: '#ededed'} }
              }
            }
          ]
        };
        vg.parse.spec(spec, function(chart) {
          var view = chart({el: self.$()[0], renderer: 'svg'})
              .update();
        });
      }.observes('data'),
    });

    Explore.PropertyView = Em.View.extend({
      didInsertElement : function(){
        console.log("YO YO YO");
        var self = this;
        Ember.run.next(function(){
          setTimeout(function(){
            var b = self.$('.ratings-affix');
            b.affix({
              offset:{
                top:function(){
                  var c = b.offset().top,
                      d = parseInt(b.children(0).css('margin-top'),10),
                      e = $('.navbar').height();
                  return this.top = c - e - d
                },
                bottom:function(){
                  return this.bottom = $('.footer').outerHeight(!0);
                }
              }
            })
          }, 100);
        });
      },
    });

  });
}(window.jQuery, window.Handlebars, window.Ember, window.d3, window.vg);
