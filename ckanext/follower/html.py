HEAD_CODE = """
<link rel="stylesheet" href="/ckanext-follower/css/main.css" 
      type="text/css" media="screen" /> 
<link rel="stylesheet" href="/ckanext-follower/css/buttons.css" 
      type="text/css" media="screen" /> 
"""

BODY_CODE = """
<script type="text/javascript" src="/ckanext-follower/jquery-1.5.2.min.js"></script>
<script type="text/javascript" src="/ckanext-follower/follower.js"></script>
<script type="text/javascript">
    $('document').ready(function($){
        CKANEXT.FOLLOWER.init('%(package_id)s', '%(package_name)s', '%(user_id)s');
    });
</script>
"""

FOLLOWER_CODE = """
<span id="follower">
<a id="package-followers"></a>
<a id="follow-button"></a>
</span>
"""

ERROR_CODE = """
<div id="follower-error"></div>
"""

PACKAGES_FOLLOWED_CODE = """
<li><strong>Packages followed:</strong> %(packages_followed)s</li>
"""
