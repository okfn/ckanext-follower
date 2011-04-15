HEAD_CODE = """
<link rel="stylesheet" href="/ckanext/follower/css/buttons.css" 
      type="text/css" media="screen" /> 
<style type="text/css">
div#follower { display: inline }
</style>
"""

BODY_CODE = """
<script type="text/javascript" src="/ckanext/follower/jquery-1.5.2.min.js"></script>
<script type="text/javascript" src="/ckanext/follower/follower.js"></script>
<script type="text/javascript">
    $('document').ready(function($){
        CKANEXT.FOLLOWER.init('%(package_id)s', '%(follower_node)s');
    });
</script>
"""

FOLLOWER_CODE = """
<div id="follower">
</div>
"""
