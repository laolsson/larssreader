
var cache = {}
/* invalidate cache every 10 min */
(function() { cache = {}; }).periodical(1000 * 60 * 10); //10 minutes

function display_feeds(){
	$.get('/json/feeds',function(r){
               render_feeds(r);
           },'json');
		   $("#testing").append("Error - got no feeds")
			}
			
function render_feeds(r) {
	var tmp = '<div id="feeds">';
	$.each(r.feeds,function(){
		var title = this.title
		if(this.unread_items > 0)
			title = '<b>' + title + '(' + this.unread_items + ')</b>'
		tmp = tmp + ('<div class="row"><a href="javascript:display_feed(' + this.key + ')">' + title + '</a> <a href="/update_feed?id=' + this.key + '">-></a></div>');	
    });
	tmp = tmp + '</div>'; 
	$("#feeds").replaceWith(tmp);	
}
	
function display_feed(id){
	$.get('/json/feed?id=' + id,function(r){
               render_feed(r);
           },'json');
		   $("#testing").append("Error - got no feeds")
			}

function render_feed(r){
		var tmp = '<div id="feed">';
		
		tmp = tmp + '<div class="row"><b>' + r.feed.title + '</b> Update: ' + r.feed.last_update + '<a href="/update_feed?id=' + r.feed.key + '">Update</a> <a href="/update_feed?id=' + r.feed.key + '">All</a><a href="/update_feed?id=' + r.feed.key + '">Unread</a></div>'
		
		$.each(r.items,function(){
			var title = this.title;
			if(!this.read)
				title = '<b>' + title + '</b>'
			tmp = tmp + ('<div class="row"><a href="javascript:toggle(' + this.id + ')">'+ title + '</a>' + this.date + '</div><div id="' + this.id + '" style="display: none">' + this.summary + '<br><br><a href="/read?id=' + this.id + ' " target="_blank"> <- Read more -> </a><br><br></div>')
        });
    tmp = tmp + '</div>';            
	$("#feed").replaceWith(tmp)
}

function toggle(elem) {
	var ele = document.getElementById(elem);
	var text = document.getElementById("displayText");
	if(ele.style.display == "block") {
    		ele.style.display = "none";
		text.innerHTML = "show";
  	}
	else {
		ele.style.display = "block";
		text.innerHTML = "hide";
	}
} 