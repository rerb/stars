function help(parent, descrip)
{
    $("div.help").remove();
    
    var node = document.createElement("div");
    
    node.className = "help";
    
    node.onclick = function()
    {
        $(this).remove();
    }
    
    node.innerHTML = descrip;
    
    parent.appendChild(node);
}

function highlightRow(element)
{
    while(element.nodeName != "TR")
    {
        element = element.parentNode;
    }
    
    element.style.backgroundColor = "#eefac5";
}

$(document).ready(function()
{
    $("tr.form input, tr.form textarea, tr.form select").focus(function()
    {
        highlightRow(this.parentNode);
    });
    
    $("tr.form input, tr.form textarea, tr.form select").blur(function()
    {
        $("tr.form").css("background-color", "#fff");
    });
})