HEAD_CODE = """
<link rel="stylesheet" href="/ckanext/follower/css/buttons.css" 
      type="text/css" media="screen" /> 
<style type="text/css">
span#follower { display: inline }
#follower-error { color: #b00 }
</style>
"""

BODY_CODE = """
<script type="text/javascript" src="/ckanext/follower/jquery-1.5.2.min.js"></script>
<script type="text/javascript" src="/ckanext/follower/follower.js"></script>
<script type="text/javascript">
    $('document').ready(function($){
        CKANEXT.FOLLOWER.init('%(package_id)s', '%(user_id)s','%(location)s');
    });
</script>
"""

FOLLOWER_CODE = """
<span id="follower">
</span>
"""
