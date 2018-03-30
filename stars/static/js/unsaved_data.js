$(document).ready(function(){

	$('a').click(function(e){

    e.preventDefault();
    var thisHref = $(this).attr('href');
    if($('#data-changed').hasClass("form-has-changed")){
      $('#unsaved-data').modal();
      $('.modal-close-button').click(function(){
        window.location.href = thisHref;
      });
    }
    else{
      window.location.href = thisHref;
    }

	});

});
