var CKANEXT = CKANEXT || {};

CKANEXT.FOLLOWER = {
    init:function(packageID, followerNodeID){
        this.packageID = packageID;
        var followerNode = $(followerNodeID);
        this.showNumFollowers(followerNode);
        this.showFollowToggle(followerNode);
    },

    showNumFollowers:function(node){
        // show the number of people following this package
        $.getJSON('/api/2/follower/package/' + this.packageID,
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

    showFollowToggle:function(node){
        // get the number of people following this package
        $.getJSON('/api/2/follower/package/' + this.packageID,
            function(data){
                var html = '<a href="HREF" class="positive-button pcb"><span>TEXT</span></a>'
                var text = "Follow";
                var followersURL = "/api/2/follower";

                html = html.replace('HREF', followersURL);
                html = html.replace('TEXT', text);
                node.append(html);
            });
    }
};
