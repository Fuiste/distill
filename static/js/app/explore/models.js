$(function(){
  //Simplicity vars
  var e = Explore;
  var m = DS.Model;
  var a = DS.attr;

  //Models
  e.Review = m.extend({
    text: a('string'),
    grade: a('number')
  });

  e.Property = m.extend({
    name: a('string'),
    reviews: DS.hasMany('review')
  });
});
