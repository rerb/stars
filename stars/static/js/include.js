
function expand_collapse_parent_parent(child_obj) {
    expand_collapse(child_obj.parentNode.parentNode);
}

function expand_collapse_parent(child_obj) {
    expand_collapse(child_obj.parentNode);
}
function expand_collapse(dom_obj) {
    /* Expand or Collapse any DOM object - usually a list or a div
       The object must contain an image tag, showing the expanded / collapsed state of the object.
       Typically triggered by onclick="expand_collapse_parent(this);" event handler on the image tag.
       Really just sets the object's class = 'expanded' or 'collapsed' - CSS does the rest.
     */
    var img_obj = dom_obj.getElementsByTagName('img')[0];
    var css_class = dom_obj.className;

    if (css_class.search(/collapsed/g) > -1) {
        img_obj.src = "/media/static/images/collapse.png";
        img_obj.title = "collapse";
        img_obj.className = "collapse";
        img_obj.alt = '-';
        dom_obj.className = css_class.replace(/collapsed/g, 'expanded');
    }
    else {
        img_obj.src = "/media/static/images/expand.png";
        img_obj.title = "expand";
        img_obj.className = "expand";
        img_obj.alt = '+';
        if (css_class.search(/expanded/g) > -1) {
            dom_obj.className = css_class.replace(/expanded/g, 'collapsed');
        }
        else {
            dom_obj.className = css_class + ' collapsed';        
        }
    }
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
        var rel = 'save_ordering';
        var buttons = table.getElementsByTagName("button");
        for (i = 0; i < buttons.length; i++) {
            if (buttons[i].hasAttribute("rel") && buttons[i].rel == rel) {
                buttons[i].disabled = false
            }
        }
        
        
        //var save_button = document.getElementById('save_ordering');
        //save_button.disabled = false;
    }
}

function show_tool_tip(tooltip) {
    tipShowing = document.getElementById('WzTtDiV').style['visibility'] != 'hidden'
    if(tipShowing) {
        UnTip();
    }
    else {
        body = "<span class='unTipIcon'><img onclick=\'UnTip();\' title=\'close\' class=\'close\' src=\'/media/static/images/grey_cross.png\'/></span><div class='innerTip'>"
               + tooltip + "</div>";
        Tip(body, WIDTH, -350, STICKY, true);
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
        if( status_obj != null && status_obj.value == 'na' ) {     // unless not applicable is selected.
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

function open_popup(url, name) {
    win = window.open(url, name, 'height=500,width=670,resizable=yes,scrollbars=yes');
    win.focus();
    return false;
}

function has_unsaved_data() {
	return !document.getElementById('submit_button').disabled;
}

function before_unload_credit() {
	if( has_unsaved_data() ) {
		return "Changes to this credit have not been saved. Discard?";
	}
}

/**
 * enable_submit() enables submission for the credit form
 * the state of the submission button is an indicator of
 * the state of the form. if the submisison button is disabled
 * then the form doesn't have any changes to be saved
 * 
 * the before_unload_credit() method uses the status of the button
 * to determine if the user should be alerted with a pop-up that
 * there have been changes made to the system
 * 
 * ignore_errors is used when the form is processed to ensure that
 * the form can be submitted without before_unload_credit() preventing
 * the user from submitting
 **/
function enable_submit(enable, ignore_errors) {
	button = document.getElementById('submit_button');
	
	re = /.*errors.*/;
	if( !ignore_errors && re.test(button.className)) {
		// If there were errors, don't disable the button
		return
	}
	
    button.disabled = !enable;
    if(enable) {
    	button.className = "enabled";
    }
    else {
    	button.className = "disabled";
    }
}

/* We may find other uses for this in future, so I abstracted it */
function field_changed(el) {
    enable_submit(true);
}
