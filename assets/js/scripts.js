
var cache = {};
var feeds_cache = 
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
		tmp = tmp + ('<div class="row"><a href="/delete_feed?id=' + this.key + '">X</a> <a href="javascript:display_feed(' + this.key +
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
		
function markas_feed(id, which_tems_bool, read){
	$.get('/markas_feed?id=' + id + '&mark=' + read,function(r){
			/* if this was successful much faster to just update cache */
			for (var i =0; i < cache[id].items.length;i++){
				if (read == 'read')
					cache[id].items[i].read = true;
				else
					cache[id].items[i].read = false;
			}
			
			if (read == 'read')
				cache[id].feed.unread_items = 0;
			else
				cache[id].feed.unread_items = cache[id].items.length;
			
			//render_feeds(cache);
			render_feed(cache[id], which_items_bool);
    },'json');
	
	$("#testing").append('<div id="feed">Error - got no feed</div>')
}
		
function render_feed(r, unread_only){
	var which_items = "Show All";
	which_items_bool = "false";
		
	if (!unread_only){
		which_items = "Show Unread";
		which_items_bool = "true";
	}
	
	if (r.feed.unread_items == 0){
		read_link = "Mark all as unread";
		read = "'unread'";
	}
	else {
		read_link = "Mark all as read";
		read = "'read'";		
	}
		
	var tmp = '<div id="feed">';		
	tmp = tmp + '<div class="row"><b>' + r.feed.title + '</b>    ' + r.feed.last_update +
				'    <a href="/update_feed?id=' + r.feed.key + '">Update</a> <a href="javascript:show_feed(' +
				r.feed.key + ',' +  which_items_bool + ')">' + which_items + '</a> <a href="javascript:markas_feed(' +
				r.feed.key + ',' + which_items_bool + ', ' + read + ')">' + read_link + '</a></div>';
	
	even = true
	$.each(r.items,function(){
		var title = this.title;
		row_class = 'row_even';
		if (even)
			row_class = 'row_uneven';
		else
			row_class = 'row_even';
		even = !even;
		row_class= 'row';
		if(!unread_only || !this.read){
			if(!this.read)
				title = '<b>' + title + '</b>'
			tmp = tmp + ('<div class="' + row_class + '"><a href="javascript:toggle(' + this.id + ')">'+ title +
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