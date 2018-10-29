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


// const delete_btn = document.querySelector('#delete_btn');

// function submitDelete() {
//   console.log('Stop clicking me!');
// }

// delete_btn.addEventListener('submit', submitDelete);
	
})