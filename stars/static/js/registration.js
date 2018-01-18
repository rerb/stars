$(document).ready(function(){

  $('.org-list li').click(function(){
    var orgName = $(this).text();
    var orgID = $(this).val();
    $('#org-name').val(orgName);
    $('#asshe_id').val(orgID);
    $('.green-dot').show();
    hideList();
    clearSearch();
  });

  $('#school-finder').focus(function(){
    showOrgs();
  });

  $('#school-finder').keyup(function(){
    orgName = $(this).val();
    $('.org-list li').each(function(){
      if ($(this).text().search(new RegExp(orgName, 'i')) < 0){
        $(this).css("display","none");
      }
      else{
        $(this).css("display","block");
      }
    });
  });


});


function showOrgs(){
  $('.org-list').css("display","block");
}

function hideList(){
  $('.org-list').css("display","none");
}

function clearSearch(){
  $('#school-finder').val('');
}
