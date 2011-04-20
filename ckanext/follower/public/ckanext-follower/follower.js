// CKAN Follower Extension
//
// This module adds the number of package followers and the follow/unfollow
// links to a CKAN package.

var CKANEXT = CKANEXT || {};

CKANEXT.FOLLOWER = {
    init:function(packageID, userID){
        this.packageID = packageID;
        this.userID = userID;
        this.isFollowing = this.isFollowingPackage();
        this.packageFollowers();
        this.followPackage(packageID, userID);
    },

    // returns true if the user (this.userID)
    // is following the package (this.packageID), 
    // returns false otherwise
    isFollowingPackage:function(){
        var isFollowing = false;
        var userID = this.userID;

        var findUser = function(data){
            for(var i = 0; i < data.length; i++){
                if(data[i].id == userID){
                    isFollowing = true;
                    break;
                }
            }
        };

        // this has to be synchronous so we know whether to display
        // 'follow' or 'unfollow' initially
        $.ajax({method: 'GET',
                url: '/api/2/follower/package/' + this.packageID,
                dataType: 'json',
                async:   false,
                success: findUser
        }); 

        return isFollowing;
    },

    // show the number of people following this package
    packageFollowers:function(){
        var packageID = this.packageID;

        $.getJSON('/api/2/follower/package/' + packageID,
            function(data){
                var html = '<a href="HREF" id="package-followers" ' +
                    'class="button pcb"><span>TEXT</span></a>'
                var text = data.length + " Following";
                var followersURL = "/api/2/follower/package/" + packageID;
                html = html.replace('HREF', followersURL);
                html = html.replace('TEXT', text);

                // replace the package followers button
                $('a#package-followers').replaceWith(html);
        });
    },

    // callback function for the follow button being clicked
    follow:function(){
        // post follow info to follower API
        followerData = {user_id: CKANEXT.FOLLOWER.userID,
                        object_type: 'package',
                        package_id: CKANEXT.FOLLOWER.packageID,
                        action: 'follow'};
        $.post("/api/2/follower", followerData,
            // successful follow
            function(response){
                // remove any existing error message
                $('div#follower-error').remove();
                // update the follower count
                CKANEXT.FOLLOWER.packageFollowers();
                // update the follow button
                CKANEXT.FOLLOWER.isFollowing = true;
                CKANEXT.FOLLOWER.followPackage();
            })
        .error(
            function(error){
                // JSON error message is contained in error.responseText
                // HTTP error code is in error.status
                var errorHtml = '<div id="follower-error">Error: ' +
                    'Could not follow this package, please try again' +
                    ' later (Error STATUS)</div>';
                errorHtml = errorHtml.replace('STATUS', error.status);
                $('div#follower-error').replaceWith(errorHtml);
        });
     },

    // callback function for the unfollow button being clicked
    unfollow:function(){
        followerData = {user_id: CKANEXT.FOLLOWER.userID,
                        object_type: 'package',
                        package_id: CKANEXT.FOLLOWER.packageID,
                        action: 'unfollow'};

        $.post("/api/2/follower", followerData,
            // successful follow
            function(response){
                // remove any existing error message
                $('div#follower-error').remove();
                // update the follower count
                CKANEXT.FOLLOWER.packageFollowers();
                // update the follow button
                CKANEXT.FOLLOWER.isFollowing = false;
                CKANEXT.FOLLOWER.followPackage();
            })
        .error(
            function(error){
                // JSON error message is contained in error.responseText
                // HTTP error code is in error.status
                var errorHtml = '<div id="follower-error">Error: ' +
                    'Could not unfollow this package, please try again' +
                    ' later (Error STATUS)</div>';
                errorHtml = errorHtml.replace('STATUS', error.status);
                $('div#follower-error').replaceWith(errorHtml);
        });
     },

    followPackage:function(){
        // if userID is not set (empty string), then just
        // display a disabled button, prompting the user 
        // to login in order to follow a package
        if(this.userID == ''){
            var html = '<a id="follow-button" class="disabled-button pcb">' +
                '<span id="follow-button-text">Login to follow packages</span></a>';
            $('a#follow-button').replaceWith(html);
            return;
        }

        // create the follow/unfollow button
        var html = '<a id="follow-button" class="pcb">' +
            '<span id="follow-button-text">TEXT</span></a>';
        var buttonText = "Follow";
        if(this.isFollowing){
            buttonText = "Unfollow";
        }
        html = html.replace('TEXT', buttonText);
        $('a#follow-button').replaceWith(html);

        // register callback functions to follow/unfollow
        if(this.isFollowing){
            $('a#follow-button').click(CKANEXT.FOLLOWER.unfollow);
            $('a#follow-button').addClass('negative-button');
            $('a#follow-button').removeClass('positive-button');
        }
        else{
            $('a#follow-button').click(CKANEXT.FOLLOWER.follow);
            $('a#follow-button').addClass('positive-button');
            $('a#follow-button').removeClass('negative-button');
        }
    }
};
