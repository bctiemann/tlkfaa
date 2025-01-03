function nop() {}

$.ajaxSetup ({
    // Disable caching of AJAX responses */
    cache: false
});

function setFilename(pendingid, filename) {
  $('#approveform_'+pendingid)[0].filename.value = filename;
}

function approvePicture(fnc,pendingid) {
//  var url = "/admin/ajax_approve.jsp?fnc=loading";
  var postform = $('#approveform_'+pendingid).serialize();
//  $('#pending_'+pendingid).load(url,function() {
  if (!$('#approveform_'+pendingid)[0].filename.value) {
    alert('Must enter a filename.');
    return;
  }

  $('#pending_'+pendingid).empty();
  $('#loading_table').clone().appendTo('#pending_'+pendingid).show();

//    url = "/admin/ajax_approve.jsp?fnc="+fnc+"&pendingid="+pendingid;
    url = '/admin/approve/' + pendingid + '/' + fnc + '/';
    $.post(url,postform,function(data) {
      $('#pending_'+pendingid).html(data);
//      url = "/admin/ajax_approve.jsp?fnc=count";
      updateCount();
      if (fnc == 'approve') {
//        url = "/admin/ajax_approve.jsp?fnc=getnew";
        url = '/admin/approve/list/';
        $.ajax({ url: url, success: function(data) {
          $('#pendinglist').empty().append(data);
        }});
      }
    });
//  });
}

function addComment(selform) {
  var newcomment = prompt("Enter comments:");
  selform.newcomments.value=newcomment;
}

function uploadThumb(pendingid,fileinput,successdiv,pausems) {
  if (!pausems) { pausems = 5000; }
  var formvars = $('#approveform_'+pendingid).serialize();
  $.ajaxFileUpload({
    url: '/api/upload.jsp?'+formvars,
    secureuri: false,
    fileElementId: fileinput,
    dataType: 'json',
    success: function (data, status) {
console.log(data);
      if (typeof data.error !== 'undefined') {
        if(data.error != '') {
          alert(data.error);
        } else {
          alert(data.msg);
        }
      } else {
        $('#'+successdiv).html('<table><tr><td>Processing picture...</td></tr></table>');
        setTimeout(function() {
//          $('#'+successdiv).html(data);
          $('#'+successdiv).load('/admin/ajax_showpending.jsp?pendingid='+pendingid);
//          $('#'+successdiv).load("/admin/ajax_approve.jsp?fnc=getnew&pendingid="+pendingid);
        },pausems);
      }
    },
    error: function (data, status, e) {
      alert(e);
    }
  });
  return false;
}

function showInfo(pendingid) {
  $('#pendinginfo_'+pendingid).show();
}

function updateCount() {
    $.getJSON('/admin/approve/count/', function(data) {
        $('#pendingcount').html(data.count);
    });
}

function autoApproval(artist_id) {
    if (confirm('Are you sure you want to give this artist auto-approval privileges?')) {
        var url = '/admin/approve/auto_approval/' + artist_id + '/';
        var params = {
            auto_approve: true,
        };
        $.post(url, params, function(data) {
            if (data.success) {
                alert('Artist successfully granted auto-approval.');
                url = '/admin/approve/list/';
                $.ajax({ url: url, success: function(data) {
                    $('#pendinglist').empty().append(data);
                }});
            } else {
                alert(data.errors);
            }
        });
    };
}

function showModNotes(artist_id) {
    var url = '/admin/approve/mod_notes/' + artist_id + '/';
    $('#dialog_mod_notes').load(url, function() {
        $('#dialog_mod_notes').dialog('open');
    });
}

function addModNote(artist_id) {
    var url = '/admin/approve/mod_notes/' + artist_id + '/add/';
    var params = {
        note: $('#note').val(),
    };
console.log(params);
    $.post(url, params, function(html) {
        $('#dialog_mod_notes').html(html);
    });
}

$(document).ready(function() {

    updateCount();

    $('#dialog_mod_notes').dialog({
        autoOpen: false,
        resizable: false,
        modal: true,
        width: 600,
        maxHeight: 600,
        position: { my: "top", at: "top+200", of: window },
    });

});
