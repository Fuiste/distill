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

  e.Property = m.extend({
    name: a('string'),
    reviews: DS.hasMany('review'),
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
    }.property('averageScore')
  });
});
