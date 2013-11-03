// Additional JS functions here
window.fbAsyncInit = function() {
    FB.init({
        appId      : '641825062515294', // App ID
        channelUrl : '/static/channel.html', // Channel File
        status     : true, // check login status
        cookie     : true, // enable cookies to allow the server to access the session
        xfbml      : true  // parse XFBML
    });

    FB.Event.subscribe('auth.authResponseChange', function(response) {
        if (response.status === 'connected') {
            $.ajax({
                url: '/token?key=' + response.authResponse.accessToken,
                success: function(data) {
                    if (data.refresh) { window.location.reload(); }
                }
            });
        } else {
            FB.login();
        }
    });
};


// Load the SDK asynchronously
(function(d){
    var js, id = 'facebook-jssdk', ref = d.getElementsByTagName('script')[0];
    if (d.getElementById(id)) {return;}
    js = d.createElement('script'); js.id = id; js.async = true;
    js.src = "//connect.facebook.net/en_US/all.js";
    ref.parentNode.insertBefore(js, ref);
}(document));
