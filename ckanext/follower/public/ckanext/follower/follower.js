// CKAN Follower Extension
//
// This module adds the number of package followers and the follow/unfollow
// links to a CKAN package.

var CKANEXT = CKANEXT || {};

CKANEXT.FOLLOWER = {
    init:function(packageID, userID, nodeID){
        var node = $(nodeID);
        this.packageFollowers(packageID, node);
        this.followPackage(packageID, userID, node);
    },

    packageFollowers:function(packageID, node){
        // show the number of people following this package
        $.getJSON('/api/2/follower/package/' + packageID,
            function(data){
                // node.append('<h3>' + data[0].username + '</h3>');
                //
                // for(user in data){
                    // node.append('<h3>' + data[user].username + '</h3>');
                // }
                var html = '<a href="HREF" class="button pcb"><span>TEXT</span></a>'
                var text = data.length + " Following";
                var followersURL = "#";
                html = html.replace('HREF', followersURL);
                html = html.replace('TEXT', text);
                node.append(html);
            });
    },

    followPackage:function(packageID, userID, node){
        // if userID is not set (empty string), then just
        // display a disabled button, prompting the user 
        // to login in order to follow a package
        
        // get the number of people following this package
        $.getJSON('/api/2/follower/package/' + packageID,
            function(data){
                var html = '<a id="follow-button" class="positive-button pcb">' +
                    '<span id="follow-button-text">TEXT</span></a>';
                var text = "Follow";
                html = html.replace('TEXT', text);
                node.append(html);

                // post follow info to follower API
                $('a#follow-button').click(function() {
                    followerData = {user_id: userID,
                                    object_type: 'package',
                                    package_id: packageID};
                    $.post("/api/2/follower", followerData,
                        function(response){
                            alert(response.status);
                            // update the button text and class
                            $('#follow-button-text').replaceWith("<span>Unfollow</span>");
                            $('#follow-button')
                                .removeClass("positive-button")
                                .addClass("negative-button");
                        })
                    .error(
                        function(error){
                            // JSON error message is contained in error.responseText
                            // HTTP error code is in error.status
                            var error_html = '<div id="follower-error">Error: ' +
                                'This package could not be followed, please try ' +
                                'again later (Error STATUS)</div>';
                            error_html = error_html.replace('STATUS', error.status);
                            
                            // if an error message already exists, replace it
                            error_node = $('#follower-error')
                            if(error_node.length > 0){
                                error_node.replaceWith(error_html);
                            }
                            // if not, create a DIV after the heading
                            else{
                                $('h2.head').after(error_html);
                            }
                        });
                });
            });
    }
};
