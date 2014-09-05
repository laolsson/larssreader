
var cache = {};
/* invalidate cache every 10 min */
(function() { cache = {}; }).periodical(1000 * 60 * 10); //10 minutes

function display_feeds(){
	$.get('/json/feeds',function(r){
               render_feeds(r);
           },'json');
	$("#feeds").replaceWith('<div id="feeds">Error - got no feeds</div>')
	}
			
function render_feeds(r) {
	var tmp = '<div id="feeds">';
	$.each(r.feeds,function(){
		var title = this.title
		if(this.unread_items > 0)
			title = '<b>' + title + '(' + this.unread_items + ')</b>'
		tmp = tmp + ('<div class="row"><a href="javascript:display_feed(' + this.key +
			')">' + title + '</a> <a href="/update_feed?id=' + this.key + '">-></a></div>');	
    });
	tmp = tmp + '</div>'; 
	$("#feeds").replaceWith(tmp);	
}
	
function display_feed(id){
	$.get('/json/feed?id=' + id,function(r){
			cache[id] = r
			render_feed(r, true);
           },'json');
	$("#testing").append('<div id="feed">Error - got no feed</div>')
	}
	
function show_feed(id, unread_only){
	render_feed(cache[id], unread_only);
}
			
function render_feed(r, unread_only){
	var which_items = "Show All";
	which_items_bool = "false";
		
	if (!unread_only){
		which_items = "Show Unread";
		which_items_bool = "true";
	}
		
	var tmp = '<div id="feed">';		
	tmp = tmp + '<div class="row"><b>' + r.feed.title + '</b>    ' + r.feed.last_update +
				'    <a href="/update_feed?id=' + r.feed.key + '">Update</a> <a href="javascript:show_feed(' +
				r.feed.key + ',' +  which_items_bool + ')">' + which_items + '</div>'
		
	$.each(r.items,function(){
		var title = this.title;
		if(!unread_only || !this.read){
			if(!this.read)
				title = '<b>' + title + '</b>'
			tmp = tmp + ('<div class="row"><a href="javascript:toggle(' + this.id + ')">'+ title +
					'</a>' + this.date + '</div><div id="' + this.id + '" style="display: none">' 
					+ this.summary + '<br><br><a href="/read?id=' + this.id +
					' " target="_blank"> <- Read more -> </a><br><br></div>')
		}
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