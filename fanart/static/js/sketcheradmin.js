function nop() {}

// Mirrors the pre-2017 Sketcher/sketcheradmin.js's own structure and
// polling cadence - see sketcher/templates/sketcher/admin.html for
// sketcherAdminUrls (populated server-side via {% url %}, since a plain
// static file can't resolve Django URL names itself).

function refreshUserList() {
    $('#userlist').load(sketcherAdminUrls.users);
}

function refreshLog() {
    var container = document.getElementById('logportletcontainer');
    $('#logportlet').load(sketcherAdminUrls.log, function() {
        container.scrollTop = container.scrollHeight;
    });
}

function refreshResetStatus() {
    $('#resetstatus').load(sketcherAdminUrls.resetStatus);
}

function refreshBanned() {
    $('#bannedartists').load(sketcherAdminUrls.banned);
}

function sketcherAdminFnc(fnc, user) {
    if (fnc === 'kick') {
        $.post(sketcherAdminUrls.kick, { username: user }, function(data) {
            $('#actionresult').html(data);
        });
    }
}

function sketcherAdminBroadcast() {
    var text = $('#broadcasttext').val();
    $.post(sketcherAdminUrls.broadcast, { text: text }, function(data) {
        $('#actionresult').html(data);
        $('#broadcasttext').val('');
    });
}

function sketcherAdminToggleReset(action) {
    // $.post's third-argument callback only fires on HTTP success - a
    // permission failure on the server (see SketcherAdminToggleResetView)
    // returns a 500, which would otherwise fail completely silently here
    // instead of surfacing anywhere, same as it did on the Java side
    // before that bug was found. .fail() reports it into #actionresult
    // like every other action on this page does.
    $.post(sketcherAdminUrls.toggleReset, { action: action })
        .done(function() {
            refreshResetStatus();
        })
        .fail(function(xhr) {
            $('#actionresult').html(xhr.responseText || 'Could not update the reset schedule.');
        });
}

function sketcherAdminBan() {
    var username = $('#banusername').val();
    var reason = $('#banreason').val();
    $.post(sketcherAdminUrls.ban, { username: username, reason: reason }, function(data) {
        $('#actionresult').html(data);
        refreshBanned();
    });
}

function sketcherAdminUnban(banId) {
    $.post(sketcherAdminUrls.unban, { ban_id: banId }, function() {
        refreshBanned();
    });
}

$(document).ready(function() {
    setInterval(refreshLog, 5000);
    setInterval(refreshUserList, 5000);
    setInterval(refreshResetStatus, 60000);

    $('#broadcasttext').keyup(function(e) {
        if (e.keyCode === 13) {
            sketcherAdminBroadcast();
        }
    });
});
