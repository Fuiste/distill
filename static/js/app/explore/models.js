$(function(){
  //Simplicity vars
  var e = Explore;
  var m = DS.Model;
  var a = DS.attr;

  //Models
  e.Review = m.extend({
    text: a('string'),
    grade: a('number'),
    htmlGrade: function(){
      var grade = this.get('grade');
      var html = "";
      while(grade>0){
        html += "<i class='fa fa-star'></i> ";
        grade--;
      }
      return html;
    }.property('grade')
  });

  e.Topic = m.extend({
    name: a('string'),
    reviews: DS.hasMany('review'),
    selected: false
  });

  e.Property = m.extend({
    name: a('string'),
    reviews: DS.hasMany('review'),
    topics: DS.hasMany('topic'),
    sortedReviews: function(){
      return this.get('reviews').sortBy('grade').reverse();
    }.property('reviews'),
    averageScore: function(){
      var score = 0;
      var num = 0;
      this.get('reviews').forEach(function(r){
        score += r.get('grade');
        num++;
      });
      score = score / num;
      return score;
    }.property('@each.reviews'),
    averageScoreHtml: function(){
      var score = this.get('averageScore');
      var html = "";
      while(score>0.5){
        html += "<i class='fa fa-star'></i> ";
        score--;
      }
      if(score>0){
        html += "<i class='fa fa-star-half'></i> ";
      }
      return html;
    }.property('averageScore'),
    distributions: function(){
      var total = 0;
      var dists = [
        {
          score: "5 star",
          grade: 5,
          num: 0,
          style: "width: 0%"
        },
        {
          score: "4 star",
          grade: 4,
          num: 0,
          style: "width: 0%"
        },
        {
          score: "3 star",
          grade: 3,
          num: 0,
          style: "width: 0%;"
        },
        {
          score: "2 star",
          grade: 2,
          num: 0,
          style: "width: 0%"
        },
        {
          score: "1 star",
          grade: 1,
          num: 0,
          style: "width: 0%"
        }
      ];
      this.get('reviews').forEach(function(r){
        dists.forEach(function(d){if(r.get('grade') == d.grade){d.num++;}});
        total++;
      });
      dists.forEach(function(d){d.style = 'width: ' + ((d.num / total) * 100) + '%';});
      return dists;
    }.property('reviews'),
    bestReview: function(){
      return this.get('sortedReviews')[0];
    }.property('@each.sortedReviews'),
    worstReview: function(){
      return this.get('sortedReviews')[this.get('sortedReviews').length-1];
    }.property('@each.sortedReviews')
  });
});
