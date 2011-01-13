
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

/**
 * These scripts address tickets #344 and #385
 * They are used to disable / enable the submit button and
 *  warn the user if they navigate away from a form that has been modified.
 * They assume: (1) there is only one form (2) the submit button has id='submit_button'
 *              (3) each form element has an onchange='field_changed(this);' handler
 * To use:
 *        - onload handler should call enable_submit(false)
 *        - onunload handler should call save_form()
**/         
function confirm_leave()
{
    if (!document.getElementById('submit_button').disabled)
        if (!confirm('This page contains unsaved data. Click OK to leave without saving or Cancel to save changes before leaving.'))
            document.forms[0].submit();
}

/**
 * Set all the links on the page to have the "onclick" action be
 * confirm_exit() unless they already have an "onclick" action
 * or have the noExit className
 */
function confirm_exit() {
	
	if(!document.getElementById('submit_button').disabled) {
		if (!confirm('This page contains unsaved data. Click OK to leave without saving or Cancel to continue editing this credit.')) {
			return false;
		}
	}
	return true;
}

function update_confirm_links() {
	links = document.getElementsByTagName("a");
//	links = [document.getElementById('clickhere')];
	re = /.*noExit.*/;
	for(var i = 0; i < links.length; i++) {
		if( links[i].onclick == null && !re.test(links[i].className) ) {
			links[i].onclick = confirm_exit;
		}
	}
}


function enable_submit(enable) {
	button = document.getElementById('submit_button');
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
