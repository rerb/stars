$(document).ready(function(){

	$('a').click(function(e){

    e.preventDefault();
    var thisHref = $(this).attr('href');

    if($('#data-changed').hasClass("form-has-changed")){
			$("#id_submission_status").val('p');
      $('#unsaved-data').modal();
      $('.modal-close-button').click(function(){
        window.location.href = thisHref;
      });
			$('.modal-stash-changes').click(function(){
				$('#myModalLabel').html("One moment...");
				$('.modal-footer').hide();
				$('#modal-p').hide();
				$('.spinner').slideDown();
        var frm = $('.submit_form');

				$.ajax({
            type: frm.attr('method'),
            url: frm.attr('action'),
            data: frm.serialize(),
            success: function (data) {

								if(data.indexOf("errorlist") >= 0){
									$('.spinner').hide();
									$('#myModalLabel').html("Errors found");
									$('#modal-p').html("It appears that there were some issues"
									  + " with the new data. If you would like to make sure that"
										+ " your changes are saved, you can validate"
										+ " them by using the save as 'In progress'"
										+ " button at the bottom of the form. Otherwise, continue"
										+ " without saving.");
									$('#modal-p').show();
									$('.modal-footer').show();
									$('.modal-stash-changes').hide();
								}
								else{
									$('.spinner').hide();
									$('.checkmark').show();
									window.location.href = thisHref;
							}

            },
            error: function(data) {
                $("#modal-p").html("Something went wrong!");
            }
        });

			});
    }
    else{
      window.location.href = thisHref;
    }

	});

});
