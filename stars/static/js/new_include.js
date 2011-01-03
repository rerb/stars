function expandCollapse(image, expandOnly) {
    id = image.id;
    obj = document.getElementById(id + "_target");
    if( obj != null ) {
        if( obj.style.display == "none" || expandOnly) {
            obj.style.display = "block";
            image.src = '/media/static/images/collapse_big.gif';
            image.alt = "-";
        }
        else {
            obj.style.display = "none";
            image.src = '/media/static/images/expand_big.gif';
            image.alt = '+';
        }
    }
}

function jumpToSubcat(cat_id, sub_id) {
    // 1 Expand Category
    // 2 Expand Subcategory
    // 3 Jump to bookmark
    
    jump = "ec_" + cat_id;
    cat_img = document.getElementById(jump);
    expandCollapse(cat_img, true);
    if( sub_id ) {
    	jump = "ec_" + cat_id + "_" + sub_id;
    	sub_img = document.getElementById(jump);
    	expandCollapse(sub_img, true);
    }
    document.location = "#" + jump;
    return false;
}

function collapseSummary() {
    /**
        Collapses the summary outline but leaves a subcategory and category
        open if an anchor has been used
        
        Anchors will be in the format "ec_<cat_id>" and "ec_<cat_id>_<sub_id>"
    **/
    
    // Parse Anchor
    anchor = self.document.location.hash;
    cat = null;
    sub = null;
    if( anchor ) {
        if( anchor.match(/ec_\d+/) ) {
            cat = anchor.split('_')[1];
        }
        if( anchor.match(/ec_\d+_\d+/) ) {
            cat = anchor.split('_')[1];
            sub = anchor.split('_')[2];
        }
    }
    images = document.getElementsByTagName('IMG');
    for(var i = 0; i < images.length; i++) {
        if( images[i].id.match("ec_.*") && images[i].id != "ec_" + cat && images[i].id != "ec_" + cat + "_" + sub ) {
            expandCollapse(images[i], false);
        }
    }
}