var MIN_LETTERS_SEARCH = 4;

function search_institution(input) {
    
    if(input.value.length >= MIN_LETTERS_SEARCH) {
        // Only run the search if there are at least three characters already
    
        url = "/dashboard/admin/gateway/find-institution/";
        url += input.value;
        search(url);
    }
    
}

function search(url) {
    target = document.getElementById('search_target');
    target.innerHTML = "<p align='center'>Loading<br/><img src='/media/static/images/loading_long_bar.gif' alt='...'/></p>";
    ajaxQuery(url, target);
}

function ajaxQuery(url, target)
{ 
    var xhr; 
    try {  xhr = new ActiveXObject('Msxml2.XMLHTTP');   }
    catch (e) 
    {
        try {   xhr = new ActiveXObject('Microsoft.XMLHTTP');    }
        catch (e2) 
        {
            try {  xhr = new XMLHttpRequest();     }
            catch (e3) {  xhr = false;   }
        }
    }

    xhr.onreadystatechange  = function()
    { 
        if(xhr.readyState  == 4)
        {
            if(xhr.status  == 200) 
                target.innerHTML = xhr.responseText; 
            else 
                target.innerHTML = "Connection failed. Please try again later. <!--Error code: " + xhr.status + "-->";
        }
    }; 

    xhr.open("POST", url, true);
    xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    xhr.send(null);
} 
