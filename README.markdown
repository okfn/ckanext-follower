CKAN Follower Extension
=======================

The Follower extension for CKAN adds the ability for users to follow
data packages.

Installation and Activation
---------------------------

To install the plugin, enter your virtualenv and install the source:

    $ pip install -e hg+http://bitbucket.org/johnglover/ckanext-follower

This will also register a plugin entry point, so you now should be 
able to add the following to your CKAN .ini file:

    ckan.plugins = follower
 
After you clear your cache and reload the site, the Follower plugin
and should be available. 
A follower count and a button to follow/unfollow packages should be
available beside the RSS subscribe link on all package pages.

Feedback
--------
Send any comments, queries, suggestions or bug reports to:
j @ johnglover dot net.
