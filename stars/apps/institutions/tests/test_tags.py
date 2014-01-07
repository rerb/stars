"""
    Test the template tags:
        - wraplinks
        
    >>> from stars.apps.institutions.templatetags.report_tags import wraplinks
    
    >>> text = "<p>Check this <a href='URL'>http://boguslink.com</a> out! <a href='url2'>Some Text here</a></p>"
    >>> print wraplinks(text, 7)
    <p>Check this <a href="URL"><br/>
    http://<br/>
    bogusli<br/>
    nk.com<br/>
    </a> out! <a href="url2"><br/>
    Some Te<br/>
    xt here<br/>
    </a></p>
"""