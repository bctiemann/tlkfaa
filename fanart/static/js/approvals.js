function nop() {}

$.ajaxSetup ({
    // Disable caching of AJAX responses */
    cache: false
});

function setFilename(pendingid) {
}

function approvePicture(fnc,pendingid) {
  var url = "/admin/ajax_approve.jsp?fnc=loading";
  var postform = $('#approveform_'+pendingid).serialize();
  $('#pending_'+pendingid).load(url,function() {
    url = "/admin/ajax_approve.jsp?fnc="+fnc+"&pendingid="+pendingid;
    $.post(url,postform,function(data) {
      $('#pending_'+pendingid).html(data);
      url = "/admin/ajax_approve.jsp?fnc=count";
      $('#pendingcount').load(url);
      if (fnc == 'approve') {
        url = "/admin/ajax_approve.jsp?fnc=getnew";
        $.ajax({ url: url, success: function(data) {
          $('#pendinglist').append(data);
        }});
      }
    });
  });
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

$(document).ready(function() {

    $.getJSON('/admin/approve/count/', function(data) {
        $('#pendingcount').html(data.count);
    });

});
