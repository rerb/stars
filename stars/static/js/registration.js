$(document).ready(function(){

  // hideList();

  $('.org-list li').click(function(){
    var orgName = $(this).text();
    console.log("fired");
    $('#org-name').val("Joey");
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
  $('.org-list').slideDown(10000);
}
