$(document).ready(function() {
$('#delete_btn').on('click', function(evt){
	let current_article_id = $('#article_id').html()
	console.log(current_article_id);
	let route_url = '/article_details/' + current_article_id
	to_delete = {
		"article_to_delete" : current_article_id
	}

$.post(route_url, to_delete, function (data) {window.location="/my_closet"});
});

$('#edit_btn').on('click', function(evt){
	let current_article_id = $('#article_id').html()
	alert(current_article_id)
	to_edit = {
		"article_to_edit" : current_article_id
	}

$.get(route_url, to_edit, function (data) {window.location="/article_edit"});
});

$('.thumbnail_img').hover(function(evt){
	// alert("HI")
	console.log(evt)
	console.log(evt.currentTarget.src)
	$('#img_lrg').attr("src", evt.currentTarget.src);

});

// const delete_btn = document.querySelector('#delete_btn');

// function submitDelete() {
//   console.log('Stop clicking me!');
// }

// delete_btn.addEventListener('submit', submitDelete);
	
})