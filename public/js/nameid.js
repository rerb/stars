/**
 * Name ID Suggest
 * Thu, 24 Jul 2008 22:46:00 GMT
 */
var nameIdSuggest =
{
    timer: null,
    url: null,
    
    init: function(url)
    {
        nameIdSuggest.url = url;
        
        $("div#nameidsuggest").css("width", $("input#nameid").width()+2+"px");

        $("input#nameid").keyup(nameIdSuggest.startTimer);
        $("body").click(nameIdSuggest.closeSuggestBox);
    },
    
    closeSuggestBox: function()
    {
        $("div#nameidsuggest").css("display", "none");
    },
    
    startTimer: function()
    {
        if(nameIdSuggest.timer != null)
        {
            window.clearTimeout(nameIdSuggest.timer);
        }
        
        nameIdSuggest.timer = window.setTimeout("nameIdSuggest.getSuggestions($('input#nameid').val())", 300);
    },
    
    getSuggestions: function(value)
    {
        if(!isNaN(value) || value.length < 3)
        {
            return;
        }
        
        $.ajax(
        { 
            type: "GET", 
            url: nameIdSuggest.url,
            data: "search=" + value,
            success: nameIdSuggest.populateSuggestBox
        });
    },
    
    createSuggestElement: function(suggest)
    {
        el = document.createElement("div");
        el.appendChild(document.createTextNode(suggest.getAttribute("name")+" ("+suggest.getAttribute("id")+")"));
        el.setAttribute("id", suggest.getAttribute("id"));
        
        $(el).click(function()
        {
            $("input#nameid").val(this.getAttribute("id"));
        });
        
        $(el).bind("mouseover mouseout", function()
        {
            $(this).toggleClass("hover");
        });
        
        return el;
    },
    
    populateSuggestBox: function(data)
    {
        $("div#nameidsuggest").empty();
        $("div#nameidsuggest").css("display", "block");
        
        var doc = data.documentElement;
        var suggests = doc.getElementsByTagName("suggest");
        
        if(suggests.length == 0)
        {
            $("div#nameidsuggest").text("No institutions found.");
        }
                    
        for(i = 0; i < suggests.length; i++)
        {
            el = nameIdSuggest.createSuggestElement(suggests[i]);
            
            $("div#nameidsuggest").append(el);
        }
    }
};