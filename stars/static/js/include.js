function collapse_expand(dom_obj) {
	var li = dom_obj.parentNode;

	var children = li.getElementsByTagName('ul');
	if( children.length > 0 ) {
		children[0].style.display = ( children[0].style.display == 'none' ) ? 'block' : 'none';
	}
	if (dom_obj.title == 'collapse') {
	    dom_obj.src = "/media/static/images/expand.png";
	    dom_obj.title = "expand";
	    dom_obj.alt = '+';
	}
	else {
	    dom_obj.src = "/media/static/images/collapse.png";
	    dom_obj.title = "collapse";
	    dom_obj.alt = '-';
    }
	//dom_obj.src = (dom_obj.src == "/media/static/images/collapse.png") ? "/media/static/images/expand.png" : "/media/static/images/collapse.png";
	//dom_obj.innerHTML = (dom_obj.innerHTML == "+") ? '-' : '+';
}

function collapse_table(a_obj) {
	var th = a_obj.parentNode;
    var tr = th.parentNode;
    var table = tr.parentNode;
	var children = table.getElementsByTagName('tr');
	for( var i = 1; i < children.length; i++ ) {
		children[i].style.display = ( children[i].style.display == 'none' ) ? '' : 'none';
	}
    
    a_obj.innerHTML = (a_obj.innerHTML == 'collapse') ? "show details" : "collapse";
}

function setTable(dndtable) {
    /***
        Sets a table as reorderable
    **/
    var table = document.getElementById(dndtable);
    tableDnD = new TableDnD();
    tableDnD.init(table);
    tableDnD.onDrop = function(table, row) {
        row.style.backgroundColor = "#fff";
        var rows = this.table.tBodies[0].rows;
        var debugStr = "rows now: ";
        for (var i=0; i<rows.length; i++) {
            debugStr += rows[i].id+" ";
        }
        document.getElementById('debug').innerHTML = 'row['+row.id+'] dropped<br>'+debugStr;
        
        //var tbody =table.getElementsByTagName("tbody");
        //var Tr =TBODY[0].getElementsByTagName("tr");
        var count = 0;
        var trs = table.getElementsByTagName("tr");
        for(var i = 0; i < trs.length; i++) {
            var tds = trs[i].getElementsByTagName("td");
            var inputs =  trs[i].getElementsByTagName("input");
            // TODO: add class search
            for( var j = 0; j < inputs.length; j++ ) {
                //alert(inputs[j].className);
                if( inputs[j].className == 'ordinal' ) {
                    inputs[j].value = count;
                    count++;
                }
                
                /*var inputs =  tds[1].getElementsByTagName("input");
                if (inputs.length > 0) {
                    inputs[0].value = i;
                }*/
            }
        }
        var save_button = document.getElementById('save_ordering');
        save_button.disabled = false;
    }
}

function show_tool_tip(tooltip) {
    tipShowing = document.getElementById('WzTtDiV').style['visibility'] != 'hidden'
    if(tipShowing) {
        UnTip();
    }
    else {
        body = "<img onclick=\'UnTip();\' title=\'close\' class=\'close\' src=\'/media/static/images/cross.png\'/>"
               + tooltip;
        Tip(body, WIDTH, -350, STICKY, true);
    }
}

function expand_new_form(span_obj) {
    img_obj = span_obj.getElementsByTagName('img')[0];
    table = document.getElementById('new_form');
    if( img_obj.alt == '+' ) {
        img_obj.src = '/media/static/images/collapse.png';
        img_obj.alt = '-';
        table.style.display = '';
    }
    else {
        img_obj.src = '/media/static/images/expand.png';
        img_obj.alt = '+';
        table.style.display = 'none';
    }
}

function selectSchool(select_obj) {
    // Changes the selected school based on the pull-down select box.
    id = select_obj[select_obj.selectedIndex].value;
    if(id != 0) {
        document.location = "/auth/select-school/" + id + "/";
    }
}

function confirm_action(message, url) {
    /***
        Prompts the user with message and if the user accepts, goes to url
    ***/
    if( confirm(message) ) {
        document.location = url;
    }
}

function toggle_applicability_reasons(status_obj) {
    /***
        If a user selects the not-applicable option for a credit submission
        then the applicability reason form field gets displayed. It's hidden, otherwise.
        
        @status_obj The form field DOM Object for the status.
    ***/
    reason_obj = document.getElementById('reason_choices')
    if( reason_obj != null ) {
        reason_obj.style.display = 'none';   // hide reasons...
        if( status_obj.value == 'na' ) {     // unless not applicable is selected.
            reason_obj.style.display = '';
        }
    }
}

function get_selected_button(nodeList) {
    for (var i=0; i < nodeList.length; i++) {
        if (nodeList[i].checked) {
            return nodeList[i];
          }
    }
    return null;
}