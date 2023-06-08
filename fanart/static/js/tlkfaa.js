function nop() {}

const globals = {
    adminAnnouncementsCount: 1,
    bulletinsCount: 0,
    shoutsCount: 0,
    adminAnnouncementsToLoad: 3,
    bulletinsToLoad: 5,
    shoutsToLoad: 10,
    scrollBottomMargin: 20,
};

var selitems = [];
var ArtistList = [];
var artistlistopen;
var ArtworkList = [];
var artworklistopen;
var CharactersList = [];
var characterslistopen;
var banneropen = false;
var sketcherboxIntvMs = 10000;
var pictureidMove = 0;
var scrollIsLoading = {
    bulletins: false,
    adminAnnouncements: false,
    shouts: false,
};


$.ajaxSetup ({
    // Disable caching of AJAX responses */
    cache: false,
    error: function(data) {
        if (data.responseJSON) {
            alert(data.responseJSON.message);
        }
    },
});


/* CSRF protection */

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
const csrftoken = getCookie('csrftoken');

function csrfSafeMethod(method) {
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});


/* Support functions */

function QueryStringToJSON() {
    const pairs = location.search.slice(1).split('&');
    const result = {};
    pairs.forEach(function(pair) {
        pair = pair.split('=');
        result[pair[0]] = decodeURIComponent(pair[1] || '');
    });
    return JSON.parse(JSON.stringify(result));
}

/*
function queryStr(ji) {
  hu = window.location.search.substring(1);
  gy = hu.split("&");
  for (i=0;i<gy.length;i++) {
    ft = gy[i].split("=");
    if (ft[0] === ji) {
      return ft[1];
    }
  }
}
*/

function switchParam(select, param) {
    const params = QueryStringToJSON();
    params[param] = select.options[select.selectedIndex].value;
    const urlparts = window.location.href.split('?');
    const url = urlparts[0] + '?' + $.param(params);
    window.location.href = url;
}

function compare(a,b) {
    if (a.name > b.name)
        return -1;
    if (a.name < b.name)
        return 1;
    return 0;
}

function validateForm(selformid,successfnc) {
  var valid = true;
  var valmsgs = [];
  $('#'+selformid).find("input,textarea").each(function(i) {
    var validate = $(this).attr('validate');
    if (typeof validate !== "undefined") {
      var vals = validate.split(',');
      for (v in vals) {
        if (vals[v] == "hasvalue") {
          if (!$(this).val()) {
            var thismsg = $(this).attr('message');
            if (!thismsg) {
              thismsg = "You must enter a value.";
            }
            valmsgs.push(thismsg);
            valid = false;
          }
        } else if (vals[v].match("^maxlen:")) {
          var maxlen = vals[v].substr(7,255);
          if ($(this).val().length > maxlen) {
            var thismsg = $(this).attr('message');
            if (!thismsg) {
              thismsg = "The string is too long (max length " + maxlen + ").";
            }
            valmsgs.push(thismsg);
            valid = false;
          }
        } else if (vals[v].match("^minlen:")) {
          var minlen = vals[v].substr(7,255);
          if ($(this).val().length < minlen) {
            var thismsg = $(this).attr('message');
            if (!thismsg) {
              thismsg = "The string is too short (min length " + minlen + ").";
            }
            valmsgs.push(thismsg);
            valid = false;
          }
        } else if (vals[v] == "pattern") {
//          var pattern = vals[v].substr(8,255);
          var pattern = $(this).attr('pattern');
          if (!$(this).val().match(pattern)) {
            var thismsg = $(this).attr('message');
            if (!thismsg) {
              thismsg = "The entered value is not valid.";
            }
            valmsgs.push(thismsg);
            valid = false;
          }
        } else if (vals[v] == "email") {
          var pattern = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$/;
          if (!$(this).val().match(pattern)) {
            var thismsg = $(this).attr('message');
            if (!thismsg) {
              thismsg = "You must enter a valid email address.";
            }
            valmsgs.push(thismsg);
            valid = false;
          }
        } else if (vals[v] == "artistname") {
          var pattern = XRegExp("^[\\p{L}0-9'\"\(\)\{\}\*\&\$\# _-]+$");
//          var pattern = XRegExp("^[\\p{L}0-9'\"\(\)\[\]\{\}\*\&\$\# ]+$");
//          var pattern = /^[a-zA-Z0-9._ -]+$/;
//          if (!$(this).val().match(pattern)) {
          if (!pattern.test($(this).val())) {
            var thismsg = $(this).attr('message');
            if (!thismsg) {
              thismsg = "The name you entered contains illegal characters.";
            }
            valmsgs.push(thismsg);
            valid = false;
          }
        } else if (vals[v] == "matchpasswd") {
          var passwd = $('input#passwd').val();
          if (!$(this).val().match(passwd)) {
            var thismsg = $(this).attr('message');
            if (!thismsg) {
              thismsg = "The two passwords did not match.";
            }
            valmsgs.push(thismsg);
            valid = false;
          }
        }
      }
    }
  });
//  if (valid || true) {
  if (valid) {
    if (successfnc) {
      eval(successfnc);
    } else {
      return true;
    }
  } else {
    $('#dialog_confirm_text').html('');
    for (i in valmsgs) {
      $('#dialog_confirm_text').append(valmsgs[i]+"<br />");
    }
    $('#dialog_confirm').dialog({
      title: 'Alert',
      resizable: false,
      modal: true,
      buttons: {
        "OK": function() {
          $(this).dialog('close');
        }
      }
    });
    return false;
  }
}


/* Site functionality */

function registerUser() {
//    var url = '/api/register.jsp';
    var url = '/Register/';
    var params = {
        fnc: 'commit',
        username: $('#newname').val(),
        password: $('#password').val(),
        password_repeat: $('#password_repeat').val(),
        email: $('#email').val(),
        is_artist: $('#is_artist').val() == '1',
        'g-recaptcha-response': $('#g-recaptcha-response').val(),
    };
console.log(params);
console.log(params.is_artist);
    $.post(url, params, function(data) {
console.log(data);
        if (data.success) {
//            set_prefsname(data.storename, data.storepass);
//            window.location.href = '/ArtManager.jsp';
            window.location.href = '/ArtManager/prefs/';
        } else {
            errorText = '';
            Object.keys(data.errors).forEach(function(key) {
                errorText += data.errors[key][0] + '\n';
//                alert(key + ':\n' + data.errors[key][0]);
                console.log(key, data.errors[key][0]);
            });
            alert(errorText);
        }
    }, 'json');
}

function refreshCharCount(sel,max,obj) {
  $('#'+obj).html(sel.value.length + " / " + max);
}

function toggleUserBox(boxName) {
    const url = `/userbox/set/`;
    if ($(`#${boxName}_toggle`).hasClass('toggleopen')) {
        $(`#${boxName}`).slideUp('fast', function() {
            const params = {
                box_name: boxName,
                is_shown: false,
            };
            $.post(url, params, function(data) {});
            $(`#${boxName}_toggle`).attr('class', 'toggle toggleclosed');
        });
    } else {
        const boxContentUrl = `/userbox/${boxName}/`;
        $(`#${boxName}`).load(boxContentUrl, function() {
            $(`#${boxName}_toggle`).attr('class', 'toggle toggleopen');
            Shadowbox.setup(`#${boxName} a.thumb`);
            $(`#${boxName}`).slideDown('fast', function() {
                const params = {
                    box_name: boxName,
                    is_shown: true,
                };
                $.post(url, params, function(data) {});
            });
        });
    }
}

function getMoreAdminAnnouncements(start, count) {
    if (!scrollIsLoading.adminAnnouncements) {
        scrollIsLoading.adminAnnouncements = true;
        const url = `/admin_announcements/${count}/${start}/`;
        $.ajax({ url: url, success: function(data) {
            const innerDiv = $('#adminannouncements_inner');
            innerDiv.addClass('bulletinsscroll');
            globals.adminAnnouncementsCount += count;
            innerDiv.find('.bulletins_content').append(data);
            $('.bulletinlink').click(function() {
                showBulletin($(this).attr('bulletin_id'));
            });
            scrollIsLoading.adminAnnouncements = false;
        }});
    }
}

function getMoreBulletins(start, count) {
    if (!scrollIsLoading.bulletins) {
        scrollIsLoading.bulletins = true;
        const url = `/bulletins/${count}/${start}/`;
        $.ajax({ url: url, success: function(data) {
            const innerDiv = $('#bulletins_inner');
            innerDiv.addClass('bulletinsscroll');
            globals.bulletinsCount += count;
            innerDiv.find('.bulletins_content').append(data);
            $('.bulletinlink').click(function() {
                showBulletin($(this).attr('bulletin_id'));
            });
            scrollIsLoading.bulletins = false;
        }});
    }
}

function getMoreShouts(artistId, start, count) {
    if (!scrollIsLoading.shouts) {
        scrollIsLoading.shouts = true;
        const url = `/shouts/${artistId}/?offset=${start}&count=${count}`;
        $.ajax({ url: url, success: function(data) {
            $('#shouts').append(data);
            globals.shoutsCount += count;
            scrollIsLoading.shouts = false;
        }});
    }
}

function getAotmForm() {
  var url = '/aotm/vote/form/';
  $('#aotmvote').load(url,function() {
    setupAutocompleteArtist($('input#artist_pick_aotm'),"doAotmVote(ui.item.artistid);");
  });
}

function getAotmVote() {
  var url = '/aotm/vote/';
  $('#aotmvote').load(url,function() {
  });
}

function doAotmVote(artistid) {
//  var url = "ajax_aotmvote.jsp?artistid="+artistid;
  var url = '/aotm/vote/';
  var params = {
    artist: artistid,
  };
  $.post(url, params, function(data) {
    $('#aotmvote').html('Voting for ' + data.username + '...');
    setTimeout('getAotmVote()', 2000);
//  $('#aotmvote').load(url,function() {
//    if (artistid == -1) {
////      setupAutocompleteArtist('aotm',"$('#aotmartistid').val(ui.item.artistid);");
//      setupAutocompleteArtist('aotm',"doAotmVote(ui.item.artistid);");
//      $('#artist_pick_aotm').focus();
//    } else if (artistid) {
//      setTimeout("doAotmVote()",2000);
//    }
  });
}

function replyPM(recptid,shoutid,bulletinid) {
    if (shoutid) {
        window.location.href = '/ArtManager/private_msgs/user/' + recptid + '/?shout_id=' + shoutid;
    } else if (bulletinid) {
        window.location.href = '/ArtManager/private_msgs/user/' + recptid + '/?bulletin_id=' + bulletinid;
    }
/*
  Shadowbox.open({
    player: 'iframe',
//    content: '/pop_viewpm.jsp?recptid='+recptid+'&replytoshout='+shoutid,
    content: '/pm/shout/' + shoutid + '/',
    width: 500,
    height: 600
  })
*/
}

function replyShout(shoutId) {
    $('#dialog_shout_reply').dialog({
        title: 'Reply to Roar',
        resizable: false,
        modal: true,
        width: '50%',
        buttons: {
            "Post": function() {
                var data = {
                    comment: $('#reply_shout').val(),
                };
                console.log(data);
                var url = `/shouts/${shoutId}/reply/`;
                $.post(url, data, function(data) {
                console.log(data);
                    if (data.success) {
                        $('#reply_shout').val('');
                        $('#dialog_shout_reply').dialog('close');
                        var shoutUrl = `/shouts/${data.shout_id}/detail/`;
                        $(`#shout_${data.shout_id}`).load(shoutUrl);
                    }
                });
            },
            Cancel: function() {
                $(this).dialog('close');
            }
        }
    });
}

function changeArtistName(name,sortname) {
//  $('#tr_newname').slideDown('slow',function() {
//    $('#tr_sortname').slideDown('slow');
//  });
  refreshNameSort(name,sortname,document.getElementById('sortname'));
  $('#newname_form').slideDown('fast');
}

function refreshNameSort(name,sortname,sel) {
  var nameParts = name.split(" ");
  for (i = sel.length; i >= 0; i--) {
    sel[i] = null;
  }
  for (i = 0; i < nameParts.length; i++) {
    if (nameParts[i] != "") {
      if (nameParts[i] == sortname) {
        sel[sel.length] = new Option(nameParts[i], nameParts[i], true, true);
      } else {
        sel[sel.length] = new Option(nameParts[i], nameParts[i]);
      }
    }
  }
}

function checkAvail(name) {
    if (name) {
        const url = `/check-name/${name}/`;
        $.getJSON(url, function(data) {
            if (data.is_available) {
                $('#newnameavailable').html('Available');
            } else {
                $('#newnameavailable').html('Taken');
            }
        });
    } else {
        $('#newnameavailable').html('');
    }
}

function addIM(imclient,imid) {
  var myimid = imid.value;
  // myimid = myimid.replace(/[^0-9a-zA-Z_@\.-]/g,"");
//  var url="ajax_imclients.jsp?op=add&imclientid="+imclient.options[imclient.selectedIndex].value+"&imid="+myimid;
  var url = '/social_media/add/';
  var params = {
    'social_media': imclient.options[imclient.selectedIndex].value,
    'identity': myimid,
  };
  $.post(url, params, function(data) {
    $('#imclients').html(data);
  });
}

function removeIM(imidid) {
//  var url = "ajax_imclients.jsp?op=remove&imidid="+imidid;
  var url = '/social_media/' + imidid + '/remove/';
  $.post(url, {}, function(data) {
    $('#imclients').html(data);
  });
}

function uploadPicture(formid,fileinput,successdiv,hideformdiv,refresh,pausems) {
  if (!pausems) { pausems = 5000; }
  var formvars = $('#'+formid).serialize();
  $('#uploadformdiv').slideUp();
//  $('#uploadformdiv')
//  .ajaxStart(function(){
//    $(this).slideUp();
//  });
  $("#loading")
  .ajaxStart(function(){
    $(this).show();
  })
  .ajaxComplete(function(){
    $(this).hide();
  });
  $.ajaxFileUpload({
    url: '/upload/?' + formvars,
//    url: '/api/upload.jsp?'+formvars,
//    url: '/ajax_upload.jsp?op='+op+'&itemid='+itemid,
    secureuri: false,
    fileElementId: fileinput,
    dataType: 'json',
    success: function (data, status) {
console.log("success");
console.log(data);
        if (data.success) {
            $('#'+successdiv).html('Processing picture...');
            checkUploadSuccess(data, successdiv, hideformdiv, refresh);
        } else {
        }
    },
    error: function (data, status, e) {
console.log("error");
      alert(e);
    }
  });
  return false;
}

function checkUploadSuccess(seedData, successdiv, hideformdiv, refresh) {
console.log(seedData);
    var url = '/api/upload_status.jsp';
    var params = {
        op: seedData.op,
        pendingid: seedData.pendingid,
     };
    $.post(url, params, function(data) {
console.log(data);
        if (data.completed) {
            $('#' + successdiv).load('/api/upload_success.jsp?' + $.param(seedData), function() {
                Shadowbox.setup('#'+successdiv+' a.shadowbox');
                $('#'+hideformdiv).slideUp('fast');
                $('#uploadformdiv').load('/ajax_uploadform.jsp',function() {
                    $(this).slideDown();
                    setupTooltipPreview();
                });
                $('#comment').val('');
                if (refresh == true) {
                    window.location=window.location;
                }
            });
            $('.pending-uploads').html(data.pending);
        } else {
            setTimeout(function() {
                checkUploadSuccess(seedData, successdiv)
            }, 2000);
        }
    }, 'json');
}

function removeProfilePic() {
  var url = '/profile-pic/remove/';
  $.post(url, {}, function(data) {
    $('#profilepic').hide();
  });
}

function removeBanner() {
//  var url = "/ajax_upload.jsp?uploadop=removebanner";
  var url = '/banner/remove/';
//  $('#banner').load(url);
  $.post(url, function(data) {
    if (data.success) {
      window.location.reload();
    }
  });
}

function acceptClaim(claimid) {
//  var url = "/ajax_edittradingtree.jsp?fnc=accept&claimid="+claimid;
  var url = '/claim/' + claimid + '/accept/';
  $.post(url, function(data) {
    $('#claim_'+claimid).html(data);
  });
}

function removeClaim(claimid) {
//  $('#dialog_confirm').attr("title","Really remove?");
  $('#dialog_confirm_text').html("Are you sure you want to remove this request?");
  $('#dialog_confirm').dialog({
    resizable: false,
    modal: true,
    buttons: {
      "Remove": function() {
        $(this).dialog('close');
//        var url = "/ajax_edittradingtree.jsp?fnc=remove&claimid="+claimid;
        var url = '/claim/' + claimid + '/remove/';
        $.post(url, {}, function(data) {
console.log(data);
          window.location.reload();
//          $('#claim_'+claimid).html(data);
        });
      },
      Cancel: function() {
        $(this).dialog('close');
      }
    }
  });
}

function clearClaim(claimid) {
  alert(claimid);
}

function removeClaimPic(claimid) {
//  var url = "/ajax_upload.jsp?uploadop=removeclaimpic&itemid="+claimid;
  var url = '/claim/' + claimid + '/upload/remove/';
  $.post(url, {}, function(data) {
    $('#claim_' + claimid).html(data);
//    $('#claimthumb_'+claimid).html(data);
//    $('#claimupload_'+claimid).slideDown('fast');
  });
//  $('#claimthumb_'+claimid).load(url,function() {
//    $('#claimupload_'+claimid).slideDown('fast');
//  });
}

function toggleSelectAll(sel,myselitems) {
  if (!myselitems) { myselitems = selitems; }
  for (i = myselitems.length - 1; i >= 0; i--) {
    document.getElementById('select_'+myselitems[i]).checked = sel.checked;
  }
}

function toggleGuidelines() {
  var status = document.getElementById('guidelines').style.display;
  if (status == "block") {
    $('#guidelines').slideUp('fast');
  } else {
    var url = "/Guidelines/";
    $('#guidelines').load(url,function() {
      $('#guidelines').slideDown('fast');
    });
  }
}

function applyFolder(selform,fnc) {
  var c = false;
  if (fnc == 'delete') {
    $('#dialog_confirm_text').html("Are you sure you want to delete this folder?");
    c = true;
  } else {
    selform.fnc.value=fnc;
    selform.submit();
  }
  if (c) {
    $('#dialog_confirm').dialog({
      resizable: false,
      modal: true,
      buttons: {
        "Delete": function() {
//          selform.fnc.value=fnc;
//          selform.submit();
          deleteFolder(globals['folderid']);
        },
        Cancel: function() {
          $(this).dialog('close');
        }
      }
    });
  }
}

function confirmActivate() {
    $('#dialog_confirm_text').html("Your artist account will be activated and displayed in the Artists listings. Are you sure?");
    $('#dialog_confirm').dialog({
        resizable: false,
        modal: true,
        buttons: {
            "Activate": function() {
                var url = $('#user_mode_form').attr('action');
                var params = {
                    is_artist: true,
                };
                $.post(url, params, function(data) {
                    console.log(data);
                    if (data.success) {
                        window.location.reload();
                    } else {
                        alert(data.message);
                    }
                }, 'json');
            },
            Cancel: function() {
                $(this).dialog('close');
            }
        }
    });
}

function confirmDeactivate() {
    $('#dialog_confirm_text').html("Your artist account will be deactivated and no longer displayed in the Artists listings. Your pictures will not be deleted, but they will not be publicly accessible. Proceed?");
    $('#dialog_confirm').dialog({
        resizable: false,
        modal: true,
        buttons: {
            "Deactivate": function() {
                var url = $('#user_mode_form').attr('action');
                var params = {
                    is_artist: false,
                };
                $.post(url, params, function(data) {
                    console.log(data);
                    if (data.success) {
                        window.location.reload();
                    } else {
                        alert(data.message);
                    }
                }, 'json');
            },
            Cancel: function() {
                $(this).dialog('close');
            }
        }
    });
}

/*
function switchFolder(sel) {
  var urlparts = window.location.href.split("?");
  var url = urlparts[0]+"?";
  var args = urlparts[1].split("&");
  var gotfolder = false;
  for (i=0;i<args.length;i++) {
    var arg = args[i].split("=");
    if (arg[0] == "folderid") {
      arg[1] = sel.options[sel.selectedIndex].value;
      gotfolder = true;
    }
    if (arg[0] == "page") {
      arg[1] = 1;
    }
    if (arg[0] != '' && arg[0] != 'fnc') {
      url += arg[0]+"="+arg[1]+"&";
    }
  }
  if (!gotfolder) {
    url += "folderid="+sel.options[sel.selectedIndex].value;
  }
  url = url.replace(/&$/g,"");
  window.location.href = url;
}
*/

//function setupMove(pictureid,folderid,page) {
function setupMove(pictureid) {
//  var url = "ajax_folderselect.jsp?mode=select&pictureid="+pictureid+"&thisfolderid="+folderid+"&selfolderid="+folderid+"&page="+page;
//  $('#movetofolder_'+pictureid).load(url,function() {
//    $(this).prop('onclick', null).off('click');
//  });
  pictureidMove = pictureid;
  $('#select_destination_folder').change(function() {
//    movePicture(pictureidMove, folderid, $(this)[0], page);
    movePicture(pictureidMove, $(this)[0]);
  });
//  document.getElementById('movetofolderlink_'+pictureid).onclick = null;
  $('#dialog_select_destination_folder').dialog({
    modal: true,
  });
}

//function movePicture(pictureid,folderid,sel,page) {
function movePicture(pictureid,sel) {
    var s = getSelectList(pictureid);
    if (s.numselected > 0) {
//        var url = '/api/movePicture.jsp';
        var url = '/ArtManager/artwork/picture/' + s.selectlist + '/move/';
        var params = {
//            folderid: folderid,
            picture_ids: s.selectlist,
            folder_id: sel.options[sel.selectedIndex].value,
//            page: page,
        }
        $.post(url, params, function(data) {
            if (data.success) {
                window.location.reload();
            } else {
                alert(data.message);
            }
        }, 'json');
    }
}

function setupEditCharacter(characterid) {
//  var url = "/ajax_editcharacter.jsp?op=form&characterid="+characterid;
  var url = '/ArtManager/characters/' + characterid + '/form/';
  $('#editcharacter_'+characterid).load(url);
}

function setupEditPending(pendingid) {
//  var url = "/ajax_editpending.jsp?op=form&pendingid="+pendingid;
  var url = '/ArtManager/pending/' + pendingid + '/edit/';
  $('#editpending_'+pendingid).load(url,function() {
    setupAutocompleteCharacter(pendingid,"tagCharacter(ui.item.characterid,'add',obj);");
    $('div.actions_menu').hide();
    $('#keywords_'+pendingid).tagsInput({
      'height': '50px',
      'defaultText': 'add new'
    });
  });
}

function setupEditPicture(pictureid) {
  var url = '/ArtManager/artwork/picture/' + pictureid + '/edit/';
  $('#editpicture_'+pictureid).load(url,function() {
    setupAutocompleteCharacter(pictureid,"tagCharacter(ui.item.characterid,'add',obj);");
//    $('div.actions_menu').hide();
    $('#keywords_'+pictureid).tagsInput({
      'height': '50px',
      'defaultText': 'add new'
    });
  });
}

function setupEditCCPic(ccpicid) {
//  var url = "/ajax_editccpic.jsp?op=form&ccpicid="+ccpicid;
  var url = '/ArtManager/artwork/coloring_picture/' + ccpicid + '/edit/';
  $('#editccpic_'+ccpicid).load(url,function(data) {
//    $('div.actions_menu').hide();
  });
}

function setupEditOffer(offerid) {
//  var url = "/ajax_editoffer.jsp?op=form&offerid="+offerid;
  var url = '/offer/' + offerid + '/edit/';
  $('#editoffer_'+offerid).load(url);
  $('div.actions_menu').hide();
}

function setupRequest(pictureid) {
//  var url = "/ajax_request.jsp?pictureid="+pictureid;
  var url = '/ArtManager/artwork/picture/' + pictureid + '/gift/form/';
  $('#editpicture_'+pictureid).load(url,function() {
    setupAutocompleteArtist($('input#artist_pick_' + pictureid), 'setRequestRecipient(ui.item.artistid)');
//    $('div.actions_menu').hide();
  });
}

function setRequestRecipient(recipient_id) {
    $('#recipient').val(recipient_id);
}

function editCharacter(characterid,charform) {
  var charactername = charform.charactername.value;
  var description = charform.description.value;
  var species = charform.species.value;
  var gender = charform.gender.options[charform.gender.selectedIndex].value;
  var storyname = charform.storyname.value;
  var storyurl = charform.storyurl.value;
//  $.post("/ajax_editcharacter.jsp",{
  $.post('/ArtManager/characters/' + characterid + '/update/', {
      op: "edit",
      characterid: characterid,
      name: charactername,
      description: description,
      species: species,
      gender: gender,
      story_title: storyname,
      story_url: storyurl
    },function(data) {
    $('#editcharacter_'+characterid).html(data);
  });
}

function editPending(pendingid,pendingform) {
  var keywords_raw = pendingform.keywords.value.split(',');
  var uniqueKeywords = [];
  $.each(keywords_raw, function(i, el) {
    if($.inArray(el, uniqueKeywords) === -1) uniqueKeywords.push(el);
  });
  var folderid = pendingform.folder.options[pendingform.folder.selectedIndex].value;
  var title = pendingform.title.value;
  var keywords = uniqueKeywords.join(',');
  var characters = pendingform.characters.value;
//  $.post("/ajax_editpending.jsp",{ 
  $.post('/ArtManager/pending/' + pendingid + '/update/', {
      op: "edit",
      pendingid: pendingid, 
      folder: folderid,
      title: title,
      keywords: keywords,
      characters: characters
    },function(data) {
      $('#pending_'+pendingid).html(data);
      $('#pending_'+pendingid+' .actions_menu a').mouseenter(function() {
        $(this).addClass('ui-state-hover');
      });
      $('#pending_'+pendingid+' .actions_menu a').mouseleave(function() {
        $(this).removeClass('ui-state-hover');
      });
  });
}

function editPicture(pictureid,pictureform) {
  var keywords_raw = pictureform.keywords.value.split(',');
  var uniqueKeywords = [];
  $.each(keywords_raw, function(i, el) {
    if($.inArray(el, uniqueKeywords) === -1) uniqueKeywords.push(el);
  });
  var title = pictureform.title.value;
  var keywords = uniqueKeywords.join(',');
  var characters = pictureform.characters.value;
  var wip = pictureform.wip.checked;
  var allowcomments = pictureform.allowcomments.checked;
  var picpublic = !pictureform.private.checked;
//  $.post("/ajax_editpicture.jsp",{
  $.post('/ArtManager/artwork/picture/' + pictureid + '/update/', {
      op: "edit",
      pictureid: pictureid,
      title: title,
      keywords: keywords,
      characters: characters,
      work_in_progress: wip,
      allow_comments: allowcomments,
      is_public: picpublic
    },function(data) {
    $('#editpicture_'+pictureid).html(data);
    if (picpublic) {
      $('#picture_'+pictureid).removeClass('privatepicture');
    } else {
      $('#picture_'+pictureid).addClass('privatepicture');
    }
  });
}

function editCCPic(ccpicid,ccpicform) {
  var comment = ccpicform.comment.value;
//  $.post("/ajax_editccpic.jsp",{ 
  $.post('/ArtManager/artwork/coloring_picture/' + ccpicid + '/update/', {
      op: "edit",
      ccpicid: ccpicid,
      comment: comment
    },function(data) {
    $('#editccpic_'+ccpicid).html(data);
  });
}

function editOffer(offerid,offerform) {
  var title = offerform.title.value;
  var comment = offerform.comment.value;
  $.post('/offer/' + offerid + '/edit/', {
      op: "edit",
      offerid: offerid, 
      title: title,
      comment: comment
    },function(data) {
    $('#editoffer_'+offerid).html(data);
  });
}

function selectOfferType(sel) {
  $('#offerselect').html($('#offerselect_'+sel.options[sel.selectedIndex].value).html());
  Shadowbox.setup('#offerselect a');
}

function chooseAdoptable(offerid,claimid,op) {
//  var url = "/ajax_editadoptable.jsp?op="+op+"&offerid="+offerid+"&claimid="+claimid;
  var url = '/claim/' + claimid + '/choose/';
  $.post(url, function(data) {
//  $('#adoptableclaims_'+offerid).load(url);
    window.location.reload();
  });
}

function postAdoptableOffer() {
    var offerform = $('#offerform_new')[0];
    var url = '/ArtManager/trading_tree/adoptable/create/';
    var params = {
        title: offerform.title.value,
        comment: offerform.comment.value,
        character: offerform.characterid.value,
    };
    $.post(url, params, function(data) {
        if (data.success) {
            window.location.href = '/ArtManager/trading_tree/adoptable/?offer_id=' + data.offer_id;
        } else {
            alert(data.message);
        }
    });
}

function submitClaim(offerid,claimform) {
  var offertype = claimform.offertype.value;
  if (offertype == 'icon') {
    var comment = claimform.comment.value;
    var refurl = claimform.refurl.value;
//    $.post("/ajax_editoffer.jsp",{
    $.post('/claim/post/',{
        op: "addclaim",
        offer: offerid,
        comment: comment,
        reference_url: refurl
      },function(data) {
//      $('#genstatus').html(data);
      window.location.reload();
    }, 'json');
  } else if (offertype == 'adoptable') {
    var comment = claimform.comment.value;
//    $.post("/ajax_editadoptable.jsp",{
    $.post('/claim/post/',{
        op: "addclaim",
        offer: offerid,
        comment: comment
      },function(data) {
//      $('#adoptableclaims_'+offerid).html(data);
//      $('#genstatus').html(data);
      window.location.reload();
    });
  }
}

function loadArtworkPicture(pictureid) {
//    $('#editpicture_' + pictureid).load('ajax_editpicture.jsp?pictureid=' + pictureid, function() {
    $('#editpicture_' + pictureid).load('/ArtManager/artwork/picture/' + pictureid + '/', function() {
//        var statusurl = '/ajax_request.jsp?op=list&pictureid=' + pictureid;
        var statusurl = '/ArtManager/artwork/picture/' + pictureid + '/gift/';
        $('#picturerequestsstatus_' + pictureid).load(statusurl);
    });
}

function doRequest(pictureid,requestform) {
    var recpt = requestform.recipient.value;
    var allfans = requestform.allfans.checked;
    var message = requestform.message.value;
//    var url = '/api/request.jsp';
    var url = '/ArtManager/artwork/picture/' + pictureid + '/gift/send/';
    var params = {
        op: 'send',
        pictureid: pictureid,
        recipient: recpt,
        all_fans: allfans,
        message: message,
    }
console.log(params);
    $.post(url, params, function(data) {
console.log(data);
        if (data.success) {
            loadArtworkPicture(pictureid);
        } else {
            alert(data.message);
        }
    }, 'json');
}

//function approveRequest(approve,theform,requestid) {
function approveRequest(requestid) {
//  theform.approve.value = approve;
//  if (requestid) {
//    theform.requestid.value=requestid;
//  }
//  theform.submit();
  var url = '/ArtManager/artwall/' + requestid + '/accept/';
  $.post(url, function(data) {
    if (data.success) {
      window.location.reload();
    } else {
      alert(data.message);
    }
  });
}

function removeSentRequest(pictureid,requestid) {
    $('#dialog_confirm_text').html('Are you sure you want to remove this picture from the recipient\'s ArtWall?');
    $('#dialog_confirm').dialog({
        resizable: false,
        modal: true,
        buttons: {
            'Remove': function() {
                $(this).dialog('close');
//                var url = "/ajax_request.jsp?op=removesent&requestid="+requestid;
//                var url = '/api/request.jsp';
                var url = '/ArtManager/artwork/picture/' + requestid + '/gift/delete/';
                var params = {
                    op: 'removesent',
                    requestid: requestid,
                };
                $.post(url, params, function(data) {
//                $('#genstatus').load(url,function() {
console.log(data);
                    if (data.success) {
//                        var statusurl = '/ajax_request.jsp?op=list&pictureid=' + pictureid;
                        var statusurl = '/ArtManager/artwork/picture/' + pictureid + '/gift/';
                        $('#picturerequestsstatus_' + pictureid).load(statusurl);
                    } else {
                        alert(data.message);
                    }
                }, 'json');
            },
            Cancel: function() {
                $(this).dialog('close');
            }
        }
    });
}

function setExamplePic(pictureid) {
  if (pictureid > 0) {
    $('#dialog_confirm_text').html("This picture will be shown along with your name in all artist listings, instead of a randomly selected picture from your gallery. Are you sure?");
  } else {
    $('#dialog_confirm_text').html("Your icon will be cleared, and your name will be listed with a randomly selected picture from your gallery. Are you sure?");
  }
  $('#dialog_confirm').dialog({
    resizable: false,
    modal: true,
    buttons: {
      "OK": function() {
        $(this).dialog('close');
//        var url = "/ajax_setexamplepic.jsp?op=set&pictureid="+pictureid;
        var url = '/ArtManager/artwork/picture/' + pictureid + '/set_example/';
//        $('.pictureiconstatus').html("");
//        $('#pictureiconstatus_'+pictureid).load(url);
        $.post(url, function(data) {
            if (data.success) {
                window.location.reload();
            } else {
                alert(data.message);
            }
        }, 'json');
      },
      Cancel: function() {
        $(this).dialog('close');
      }
    }
  });
}

function getSelectList(itemid,myselitems) {
  var selectlist = '';
  var numselected = 0;
  if (!myselitems) { myselitems = selitems; }
  if (itemid == 0) {
    var selectedIds = [];
    for (i = myselitems.length - 1; i >= 0; i--) {
      if (document.getElementById('select_'+myselitems[i]).checked == true) {
//        selectlist += myselitems[i]+",";
        selectedIds.push(myselitems[i]);
        numselected++;
      }
    }
    selectlist = selectedIds.join(',');
  } else {
    selectlist = itemid;
    numselected = 1;
  }
  return {selectlist : selectlist, numselected : numselected};
}

//function deletePicture(pictureid,folderid,page) {
function deletePicture(pictureid) {
  var s = getSelectList(pictureid);
  if (s.numselected > 0) {
    if (s.numselected > 1) {
      $('#dialog_confirm_text').html("The selected "+s.numselected+" pictures will be permanently deleted. Are you sure?");
    } else {
      $('#dialog_confirm_text').html("The selected picture will be permanently deleted. Are you sure?");
    }
    $('#dialog_confirm').dialog({
      title: 'Really delete?',
      resizable: false,
      modal: true,
      buttons: {
        "Delete": function() {
//          window.location.href = "/ArtManager.jsp?op=artwork&fnc=delete&folderid="+folderid+"&picturelist="+s.selectlist+"&page="+page;
          var url = '/ArtManager/artwork/picture/' + s.selectlist + '/delete/';
          $.post(url, function(data) {
              if (data.success) {
                  window.location.reload();
              }
          });
        },
        Cancel: function() {
          $(this).dialog('close');
        }
      }
    });
  } else {
    $('div.actions_menu').hide();
  }
}

function deletePending(pendingid) {
  var s = getSelectList(pendingid);
  if (s.numselected > 0) {
    if (s.numselected > 1) {
      $('#dialog_confirm_text').html("Are you sure you want to delete these "+s.numselected+" pending pictures?");
    } else {
      $('#dialog_confirm_text').html("Are you sure you want to delete this pending picture?");
    }
    $('#dialog_confirm').dialog({
      title: 'Really delete?',
      resizable: false,
      modal: true,
      buttons: {
        "Delete": function() {
//          window.location.href = "/ArtManager.jsp?op=pending&fnc=delete&picturelist="+s.selectlist;
          var url = '/ArtManager/pending/' + pendingid + '/delete/';
          $.post(url, function(data) {
              if (data.success) {
                  window.location.reload();
              }
          });
        },
        Cancel: function() {
          $(this).dialog('close');
        }
      }
    });
  } else {
    $('div.actions_menu').hide();
  }
}

function deleteCCPic(pictureid,page) {
  var s = getSelectList(pictureid);
  if (s.numselected > 0) {
    if (s.numselected > 1) {
      $('#dialog_confirm_text').html("The selected "+s.numselected+" Coloring Cave pictures will be permanently deleted. Are you sure?");
    } else {
      $('#dialog_confirm_text').html("The selected Coloring Cave picture will be permanently deleted. Are you sure?");
    }
    $('#dialog_confirm').dialog({
      title: 'Really delete?',
      resizable: false,
      modal: true,
      buttons: {
        "Delete": function() {
          var url = '/ArtManager/artwork/coloring_picture/' + s.selectlist + '/delete/';
          $.post(url, function(data) {
            if (data.success) {
                window.location.reload();
            }
          });
//          window.location.href = "/ArtManager.jsp?op=artwork&fnc=deletecc&folderid=-1&ccpiclist="+s.selectlist+"&page="+page;
        },
        Cancel: function() {
          $(this).dialog('close');
        }
      }
    });
  } else {
    $('div.actions_menu').hide();
  }
}

function removeRequest(requestid) {
  var s = getSelectList(requestid);
  if (s.numselected > 0) {
    if (s.numselected > 1) {
      $('#dialog_confirm_text').html("Are you sure you want to remove all "+s.numselected+" selected pictures from your ArtWall?");
    } else {
      $('#dialog_confirm_text').html("Are you sure you want to remove this picture from your ArtWall?");
    }
    $('#dialog_confirm').dialog({
      title: 'Really remove?',
      resizable: false,
      modal: true,
      buttons: {
        "Remove": function() {
//          window.location.href = "/ArtManager.jsp?op=requests&fnc=remove&requestlist="+s.selectlist;
//          var url = '/ArtManager/artwork/picture/' + requestid + '/gift/delete/';
          var url = '/ArtManager/artwall/' + s.selectlist + '/delete/';
          $.post(url, function(data) {
            if (data.success) {
                window.location.reload();
            }
          }, 'json');
        },
        Cancel: function() {
          $(this).dialog('close');
        }
      }
    });
  } else {
    $('div.actions_menu').hide();
  }
}

function markRead(type,showall,myselitems) {
  if (!myselitems) { myselitems = selitems; }
  var s = getSelectList(0,myselitems);
  if (s.numselected > 0) {
    if (s.numselected > 1) {
      $('#dialog_confirm_text').html("Are you sure you want to mark all " + s.numselected + " selected " + type + "s as read?");
    } else {
      $('#dialog_confirm_text').html("Are you sure you want to mark the selected " + type + " as read?");
    }
    $('#dialog_confirm').dialog({
//      title: 'Mark read?',
      resizable: false,
      modal: true,
      buttons: {
        "Mark Read": function() {
          var url = '/ArtManager/' + type + 's/mark_read/';
          var params = {
              'comment_ids': s.selectlist,
          };
          $.post(url, params, function(data) {
            window.location.reload();
          });
//          window.location.href = "/ArtManager.jsp?op=" + type + "s&fnc=markread&type=received&showall=" + showall + "&itemlist="+s.selectlist;
        },
        Cancel: function() {
          $(this).dialog('close');
        }
      }
    });
  }
}

function movePMs(fnc,box) {
  var s = getSelectList(0);
  if (s.numselected > 0) {
    if (s.numselected > 1) {
      $('#dialog_confirm_text').html("Are you sure you want to " + fnc + " all " + s.numselected + " messages?");
    } else {
      $('#dialog_confirm_text').html("Are you sure you want to " + fnc + " the selected message?");
    }
    $('#dialog_confirm').dialog({
//      title: 'Move PMs?',
      resizable: false,
      modal: true,
      buttons: {
        "OK": function() {
//          var url = "ajax_pms.jsp?pmlist="+s.selectlist+"&fnc="+fnc;
          var url = '/pms/' + fnc + '/';
          var params = {
            'pm_ids': s.selectlist,
          };
          $.post(url, params, function(data) {
console.log(data);
          refreshPMBox(pageParams.pmbox, pageParams.page, pageParams.viewmode, pageParams.showpages, pageParams.showstatus);
          $('#dialog_confirm').dialog('close');
//          $('#pmstatus').load(url,function() {
//            window.location.href = "/ArtManager.jsp?op=privatemsgs&box="+box;
          });
        },
        Cancel: function() {
          $(this).dialog('close');
        }
      }
    });
  }
}

function removeCCPic(ccpicid, ccid) {
  $('#dialog_confirm_text').html("Are you sure you want to remove this colored picture from the Coloring Cave?");
  $('#dialog_confirm').dialog({
    resizable: false,
    modal: true,
    buttons: {
      "Remove": function() {
        $(this).dialog('close');
//        var url = "/ajax_editccpic.jsp?op=remove&ccpicid=" + ccpicid;
        var url = '/coloring/' + ccpicid + '/remove/';
        $.post(url, {}, function(data) {
//        $('#genstatus').load(url,function() {
          $('#cc_' + ccid).html(data);
//          window.location.reload();
        });
      },
      Cancel: function() {
        $(this).dialog('close');
      }
    }
  });
}

function removeOffer(offerid,offertype) {
  $('#dialog_confirm_text').html("Are you sure you want to remove this offer from the Trading Tree?");
  $('#dialog_confirm').dialog({
    resizable: false,
    modal: true,
    buttons: {
      "Remove": function() {
//        var url = "/ArtManager.jsp?op=tradingtree&fnc=remove&offerid=" + offerid + "&offertype=" + offertype;
        var url = '/offer/' + offerid + '/remove/';
        $.post(url, function(data) {
          if (data.success) {
            window.location.reload();
          }
        });
//        window.location.href = url;
      },
      Cancel: function() {
        $(this).dialog('close');
      }
    }
  });
}

function deleteCharacter(characterid) {
  $('#dialog_confirm_text').html("Are you sure you want to delete this character?");
  $('#dialog_confirm').dialog({
    title: 'Really delete?',
    resizable: false,
    modal: true,
    buttons: {
      "Delete": function() {
//        var url = "/ArtManager.jsp?op=characters&fnc=delete&characterid=" + characterid;
        var url = '/ArtManager/characters/' + characterid + '/delete/';
//        window.location.href = url;
        $.post(url, function(data) {
          if (data.success) {
            window.location.reload();
          }
        });
      },
      Cancel: function() {
        $(this).dialog('close');
      }
    }
  });
}

function selectPicture(pictureid,picturetype) {
//  window.parent.document.pickpictureform.pictureid.value = pictureid;
//  window.parent.document.pickpictureform.picturetype.value = picturetype;
  var pickpictureitem = window.parent.pickpictureform.item.value;
  var pickpictureitemid = window.parent.pickpictureform.itemid.value;
console.log($('#picker_image_' + pictureid).attr('src'));
  $('#pickpicture_'+pickpictureitemid,window.parent.document).empty().append($('<img>', {
    src: $('#picker_image_' + pictureid).attr('src'),
    class: 'thumb',
  })).closest('form').find('input[name=picture]').val(pictureid);

  if (pickpictureitem == 'character') {
//    var url = "/ajax_setpicture.jsp?pictureid="+pictureid+"&picturetype="+picturetype+"&item="+pickpictureitem+"&itemid="+pickpictureitemid;
    var url = '/ArtManager/characters/' + pickpictureitemid + '/set_picture/';
    var params = {
      picture_type: picturetype,
      picture_id: pictureid,
    };
    $.post(url, params, function(data) {
console.log(data);
      window.parent.Shadowbox.close();
    });
  } else {
    window.parent.Shadowbox.close();
  }

//  $('#pickpicture_'+pickpictureitemid,window.parent.document).load(url,function() {
//    window.parent.Shadowbox.close();
//  });
}

function selectCharacter(characterid) {
  window.parent.document.offerform_new.characterid.value = characterid;
  $('#charactername',window.parent.document).html($('#charactername_'+characterid).html());
  window.parent.Shadowbox.close();
}

function setupTagCharacters(pictureid,obj) {
//  var url = "/ajax_tagcharacters.jsp?obj="+obj;
  var url = '/ArtManager/artwork/tag_characters/' + obj + '/';
  if (pictureid) {
    url += "&pictureid="+pictureid
  }
  $('#tagcharacters_'+obj).load(url,function() {
    $('#tagcharacters_'+obj).slideDown('fast');
    setupAutocompleteCharacter(obj,"tagCharacter(ui.item.characterid,'add',obj);");
    $('a.tagcharacters').hide();
  });
}

function postContestEntry(picform) {
    if (picform.picture.value) {
        picform.submit();
    }
}

function postSelectedPic(picform) {
//  if (typeof picform.picture !== "undefined") {
  if (picform.picture.value) {
    var url = '/ArtManager/coloring_cave/' + picform.picture.value + '/post/';
    $.post(url, function(data) {
      if (data.success) {
        window.location.href = '/ArtManager/coloring_cave/' + data.coloring_base_id + '/';
      } else {
        alert(data.message);
      }
    });
//    picform.submit();
  } else {
    $('#dialog_confirm_text').html('You must select one of your pictures to post into the Coloring Cave.');
    $('#dialog_confirm').dialog({
      title: 'Alert',
      resizable: false,
      modal: true,
      buttons: {
        "OK": function() {
          $(this).dialog('close');
        }
      }
    });
  }
}

function removeColoringBase(coloringbaseid) {
  var url = '/ArtManager/coloring_cave/' + coloringbaseid + '/remove/';
  $.post(url, function(data) {
    if (data.success) {
      window.location.href = '/ArtManager/coloring_cave/';
    }
  });
}

function restoreColoringBase(coloringbaseid) {
  var url = '/ArtManager/coloring_cave/' + coloringbaseid + '/restore/';
  $.post(url, function(data) {
    if (data.success) {
      window.location.href = '/ArtManager/coloring_cave/' + coloringbaseid + '/';
    }
  });
}

/*
function enterContestPic(contestid, pictureid) {
  var url = '/contests/' + contestid + '/entry/create/';
  var params = {
    picture = pictureid,
  };
  $.post(url, params, function(data) {
    if (data.success) {
      window.location.reload();
    }
  });
}
*/

function refreshBannerPreview(selform) {
  var url = '/ArtManager/customize/banner_preview/';
  var params = {
    banner_text: selform.banner_text.value,
  };
  $.post(url, params, function(data) {
    $('#bannertextpreview').html(data);
  });
/*
  var bannertext = selform.banner_text.value;
  bannertext = bannertext.replace(/\n/g,"<br />");
//  bannertext = bannertext.replace(/(?!<![=\"])(https?|ftp|file)(:\/\/[-a-zA-Z0-9+&@#/%?=~_|!:,.;]*[-a-zA-Z0-9+&@#\/%=~_|])/gi,"<a href=\"$1$2\">$1$2</a>");
//  bannertext = bannertext.replace(/(https?|ftp|file)(:\/\/[-a-zA-Z0-9+&@#/%?=~_|!:,.;]*[-a-zA-Z0-9+&@#\/%=~_|])/gi,"<a href=\"$1$2\">$1$2</a>");
//  bannertext = bannertext.replace(/(^|[^">])(https?|ftp|file)(:\/\/[-a-zA-Z0-9+&@#/%?=~_|!:,.;]*[-a-zA-Z0-9+&@#\/%=~_|])/gm, "<a href=\"$1$2\">$1$2</a>");
  bannertext = parseBBCode(bannertext);
  $('#bannertextpreview').html(bannertext);
*/
}

function parseBBCode(intext) {
  var outtext = intext;
  outtext = outtext.replace(/\[b\](.+?)\[\/b\]/gi, "<strong>$1</strong>");
  outtext = outtext.replace(/\[i\](.+?)\[\/i\]/gi, "<span style='font-style:italic;'>$1</span>");
  outtext = outtext.replace(/\[u\](.+?)\[\/u\]/gi, "<span style='text-decoration:underline;'>$1</span>");
  outtext = outtext.replace(/\[h1\](.+?)\[\/h1\]/gi, "<h1>$1</h1>");
  outtext = outtext.replace(/\[h2\](.+?)\[\/h2\]/gi, "<h2>$1</h2>");
  outtext = outtext.replace(/\[h3\](.+?)\[\/h3\]/gi, "<h3>$1</h3>");
  outtext = outtext.replace(/\[h4\](.+?)\[\/h4\]/gi, "<h4>$1</h4>");
  outtext = outtext.replace(/\[h5\](.+?)\[\/h5\]/gi, "<h5>$1</h5>");
  outtext = outtext.replace(/\[h6\](.+?)\[\/h6\]/gi, "<h6>$1</h6>");
  outtext = outtext.replace(/\[quote\](.+?)\[\/quote\]/gi, "<blockquote>$1</blockquote>");
  outtext = outtext.replace(/\[p\](.+?)\[\/p\]/gi, "<p>$1</p>");
  outtext = outtext.replace(/\[p=(.+?),(.+?)\](.+?)\[\/p\]/gi, "<p style='text-indent:$1px;line-height:$2%;'>$3</p>");
  outtext = outtext.replace(/\[center\](.+?)\[\/center\]/gi, "<div align='center'>$1</div>");
  outtext = outtext.replace(/\[align=(.+?)\](.+?)\[\/align\]/gi, "<div align='$1'>$2</div>");
  outtext = outtext.replace(/\[color=(.+?)\](.+?)\[\/color\]/gi, "<span style='color:$1;'>$2</span>");
  outtext = outtext.replace(/\[size=(.+?)\](.+?)\[\/size\]/gi, "<span style='font-size:$1;'>$2</span>");
  outtext = outtext.replace(/\[img\](.+?)\[\/img\]/gi, "<img src='$1' />");
  outtext = outtext.replace(/\[img=(.+?),(.+?)\](.+?)\[\/img\]/gi, "<img width='$1' height='$2' src='$3' />");
  outtext = outtext.replace(/\[email\](.+?)\[\/email\]/gi, "<a href='mailto:$1'>$1</a>");
  outtext = outtext.replace(/\[email=(.+?)\](.+?)\[\/email\]/gi, "<a href='mailto:$1'>$2</a>");
  outtext = outtext.replace(/\[url\](.+?)\[\/url\]/gi, "<a href='$1'>$1</a>");
  outtext = outtext.replace(/\[url=(.+?)\](.+?)\[\/url\]/gi, "<a href='$1'>$2</a>");
  outtext = outtext.replace(/\[youtube\](.+?)\[\/youtube\]/gi, "<object width='640' height='380'><param name='movie' value='http://www.youtube.com/v/$1'></param><embed src='http://www.youtube.com/v/$1' type='application/x-shockwave-flash' width='640' height='380'></embed></object>");
  outtext = outtext.replace(/\[video\](.+?)\[\/video\]/gi, "<video src='$1' />");
  return outtext;
}

function setupAutocompleteArtist(obj,selectfn) {
  obj.autocomplete({
    source: function(request, response) {
      $.ajax({
//        url: "/ajax_ac_artists.jsp",
        url: '/artists-ac/' + request.term,
        dataType: "json",
        data: {
//          term: request.term
        },
        success: function(data) {
          response($.map(data.artists, function(item) {
            return {
              name: he.decode(item.name),
              artistid: item.artistid,
              dirname: item.dirname,
              userid: item.userid,
              label: he.decode(item.name),
              value: he.decode(item.name)
            }
          }))
        }
      })
    },
    minLength: 3,
    select: function(e,ui) {
      eval(selectfn);
    }
  });
}

function setupAutocompleteCharacter(obj,selectfn) {
  $('input#character_pick_'+obj).autocomplete({
    source: function(request, response) {
      $.ajax({
//        url: "/ajax_ac_characters.jsp",
        url: '/characters-ac/' + request.term,
        dataType: "json",
        data: {
//          term: request.term
        },
        success: function(data) {
          response($.map(data.characters, function(item) {
            return {
              value: he.decode(item.name) + " ("+he.decode(item.artistname)+")",
              characterid: item.characterid,
              name: he.decode(item.name),
            }
          }))
        }
      })
    },
    minLength: 1,
    select: function(e,ui) {
      eval(selectfn);
    }
  });
}

function setupAutocompleteSpecies(obj,selectfn) {
  $('input#species_pick_'+obj).autocomplete({
    source: function(request, response) {
      $.ajax({
//        url: "/ajax_ac_species.jsp",
        url: '/species-ac/' + request.term,
        dataType: "json",
        data: {
//          term: request.term
        },
        success: function(data) {
          response($.map(data.specieses, function(item) {
            return {
//              value: item.species+" ("+item.count+")",
              value: item.species,
              species: item.species
            }
          }))
        }
      })
    },
    minLength: 3,
    select: function(e,ui) {
      eval(selectfn);
    }
  });
}

function tagCharacter(characterid,fnc,obj) {
  var taglist = $('#characterstagged_'+obj).val();
  var newtaglist = [];
  var Tagged = taglist.split(",");
  for (i = Tagged.length - 1; i >= 0; i--) {
    if (Tagged[i] != characterid && Tagged[i] != "") {
      newtaglist.push(Tagged[i]);
    }
  }
  if (fnc == 'add') {
    newtaglist.push(characterid);
  }
//  var url = "/ajax_tagcharacters.jsp?obj="+obj+"&taglist="+newtaglist.join(',')+"&op=update";
  var url = '/ArtManager/artwork/tag_characters/' + obj + '/?taglist=' + newtaglist.join(',');
console.log(url);
  $('#tagcharacters_'+obj).load(url,function() {
//    $('#tagcharacters_'+obj).slideDown('fast');
    setupAutocompleteCharacter(obj,"tagCharacter(ui.item.characterid,'add',obj);");
//    $('a.tagcharacters').hide();
  });
//  $('#charactertaglist_'+obj).load(url, function(data) {
//    $('input#character_pick_'+obj).val('');
//    $('select#canoncharacter_pick_'+obj).val(0);
//    $('select#yourcharacter_pick_'+obj).val(0);
//  });
}

function updateCharacterList(list,term,page) {
  var url = `/Characters/search/?list=${list}&term=${escape(term)}&page=${page}`;
  console.log(url);
//  var url = "/ajax_listcharacters.jsp?mode=fan&list="+list+"&term="+escape(term)+"&page="+page;
  window.location = url;
//  $('#characterlist').load(url);
}

function filterCharacter(newcharacterid,fnc) {
  var chars = otherchars.split(',');
  var newchars = "";
  for (c in chars) {
    if (chars[c] != '' && chars[c] != newcharacterid) {
      if (newchars != "") {
        newchars += ",";
      }
      newchars += chars[c];
    }
  }
  if (fnc == 'add') {
    if (newchars != "") {
      newchars += ",";
    }
    newchars += newcharacterid;
  }
  var url='/character/' + characterid + '/?othercharacters=' + newchars;
  window.location=url;
}

function postBulletin() {
    var url = '/ArtManager/bulletins/create/';
    var params = {
        title: $('#title_new').val(),
        bulletin: $('#bulletin_new').val(),
        allow_replies: $('#allow_replies_new').prop('checked'),
    };
    $.post(url, params, function(data) {
        if (data.success) {
            window.location.reload();
        }
    });
}

function updateBulletin(bulletinid) {
    var url = '/ArtManager/bulletins/' + bulletinid + '/update/';
    var params = {
        title: $('#title_' + bulletinid).val(),
        bulletin: $('#bulletin_' + bulletinid).val(),
        allow_replies: $('#allow_replies_' + bulletinid).prop('checked'),
    };
    $.post(url, params, function(data) {
        if (data.success) {
            window.location.reload();
        }
    });
}

function deleteBulletin(bulletinid) {
  $('#dialog_confirm_text').html("Are you sure you want to delete this bulletin?");
  $('#dialog_confirm').dialog({
    resizable: false,
    modal: true,
    buttons: {
      "Delete": function() {
        var url = '/ArtManager/bulletins/' + bulletinid + '/delete/';
        var params = {};
        $.post(url, params, function(data) {
          if (data.success) {
            window.location.reload();
          }
        });
      },
      Cancel: function() {
        $(this).dialog('close');
      }
    }
  });
}

function deleteBulletin_old(selform,bulletin) {
  $('#dialog_confirm_text').html("Are you sure you want to delete this bulletin?");
  $('#dialog_confirm').dialog({
    resizable: false,
    modal: true,
    buttons: {
      "Delete": function() {
        selform.fnc.value = "delete";
        selform.submit();
      },
      Cancel: function() {
        $(this).dialog('close');
      }
    }
  });
}

function toggleFave(id,type) {
  var isfave = $('#togglefave'+type+'_'+id).hasClass('isfave');
  if (type == 'picture') {
//    var url = "/ajax_fave.jsp?pictureid="+id;
    var url = '/fave/picture/' + id + '/';
//    var faveurl = "/ajax_favoritepicturesbox.jsp";
    var faveurl = '/userbox/favorite_pictures_box/';
  } else if (type == 'artist') {
//    var url = "/ajax_fave.jsp?artistid="+id;
    var url = '/fave/artist/' + id + '/';
    var faveurl = '/userbox/favorite_artists_box/';
  }
//  $('#togglefave'+type+'_'+id).load(url,function() {
  $.post(url, function(data) {
    if (isfave) {
      $('#togglefave'+type+'_'+id).removeClass('isfave');
      $('#togglevisible_'+id).removeClass('isvisible');
    } else {
      $('#togglefave'+type+'_'+id).addClass('isfave');
    }
    $('#favorite_'+type+'s_box').load(faveurl,function() {
      if (type == 'picture') {
        Shadowbox.setup('#favoritepicturesbox a');
      } else if (type == 'artist') {
        $('#togglevisible_'+id).toggle();
      }
    });
  }, 'json');
}

function toggleVisible(id) {
//  var url = "/ajax_fave.jsp?artistid="+id+"&visible=1";
  var url = '/visible/' + id + '/';
//  var faveurl = "/ajax_favoriteartistsbox.jsp";
  var faveurl = '/userbox/favorite_artists_box/';
  var params = {
    is_visible: !($('#togglevisible_'+id).hasClass('isvisible')),
  };
  $.post(url, params, function(data) {
//  $('#togglevisible_'+id).load(url,function() {
    if (params.is_visible) {
      $('#togglevisible_'+id).addClass('isvisible');
    } else {
      $('#togglevisible_'+id).removeClass('isvisible');
    }
    $('#favorite_artists_box').load(faveurl);
  });
}

function toggleComments(pictureid) {
  var status = document.getElementById('comments_'+pictureid).style.display;
  if (status == "block") {
    $('#comments_'+pictureid).slideUp('fast');
  } else {
//    var url = "/ajax_comments.jsp?pictureid="+pictureid;
    var url = "/comments/" + pictureid;
    $('#comments_'+pictureid).load(url,function() {
      $('#comments_'+pictureid).slideDown('fast');
    });
  }
}

function toggleCCPics(ccid) {
  var status = document.getElementById('cc_'+ccid).style.display;
  if (status == "block") {
    $('#cc_'+ccid).slideUp('fast');
  } else {
//    var url = "/ajax_colored.jsp?pictureid="+pictureid+"&showcclink=1";
    var url = '/coloring/' + ccid + '/';
    $('#cc_'+ccid).load(url,function() {
      $('#cc_'+ccid).slideDown('fast');
    });
  }
}

function togglePicFans(pictureid) {
  var status = document.getElementById('picfans_'+pictureid).style.display;
  if (status == "block") {
    $('#picfans_'+pictureid).slideUp('fast');
  } else {
//    var url = "/ajax_picturefans.jsp?pictureid="+pictureid;
    var url = '/picture/' + pictureid + '/fans/';
    $('#picfans_'+pictureid).load(url,function() {
      $('#picfans_'+pictureid).slideDown('fast');
    });
  }
}

function doReply(pictureid,commentid) {
  $('#comment_'+commentid+' .commentbuttons').fadeOut('fast');
  $('#reply_'+commentid).slideDown('fast',function() {
//    document.getElementById('replybutton_'+commentid).onclick = function() { postReply(pictureid,commentid) };
  });
}

function cancelReply(pictureid,commentid) {
  $('#comment_'+commentid+' .commentbuttons').fadeIn('fast');
  $('#reply_'+commentid).slideUp('fast',function() {
//    document.getElementById('replybutton_'+commentid).onclick = function() { postReply(pictureid,commentid) };
  });
}

function postReply(pictureid,commentid) {
  var reply;
  if (commentid == 0) {
    reply = document.getElementById('replytext_picture_'+pictureid).value;
  } else {
    reply = document.getElementById('replytext_'+commentid).value;
  }
  var url = '/comments/' + pictureid + '/reply/';
  $.post(url,{ op: "post", picture: pictureid, reply_to: commentid || null, comment: reply, hash: $('#hash').val() },function(response_html) {
    $('#comments_'+pictureid).html(response_html);
  });
}

function postBulletinReply(bulletinid,commentid) {
  var reply;
  if (commentid == 0) {
    reply = document.getElementById('replytext_bulletin_'+bulletinid).value;
  } else {
    reply = document.getElementById('replytext_'+commentid).value;
  }
  var url = '/bulletin/' + bulletinid + '/reply/';
  $.post(url,{ op: "post", bulletin: bulletinid, picture: null, reply_to: commentid || null, comment: reply, hash: $('#hash').val() },function(response_html) {
    $('#comments_'+bulletinid).html(response_html);
  });
}

function postShout(artistid) {
  var shout;
  shout = document.getElementById('shouttext_'+artistid).value;
  var url = '/shouts/' + artistid + '/post/';
  $.post(url,{ op: "post", artist: artistid, comment: shout, offset: 0, count: 10 },function(data) {
console.log(data);
    var refreshurl = '/shouts/' + data.artist_id + '/?shoutid=' + data.shout_id;
    $.get(refreshurl, function(html) {
      $('#shouts').prepend(html);
      $('#shouttext_'+artistid).val('');
    });

//    $('#shouts').html(data);
  }, 'json');
}

function setupEditComment(pictureid,commentid) {
//    $.getJSON('/api/comment.jsp?commentid=' + commentid, function(data) {
    $.getJSON('/comment/' + commentid + '/detail/', function(data) {
        if (data.success) {
            $('#comment_'+commentid+' .commentbuttons').fadeOut('fast');
            $('#commenttext_' + commentid + ' .comment-edited').empty();
            $('#commenttext_' + commentid + ' .comment-text-hidden').html($('#commenttext_' + commentid + ' .comment-text').html());
            $('#commenttext_' + commentid + ' .comment-text').empty().append($('<textarea>', {
                id: 'commentedit_' + commentid,
                html: data.comment.comment,
            })).append($('<br>')).append($('<button>', {
                class: 'small',
                html: 'Submit',
                commentid: commentid,
                pictureid: pictureid,
                click: function() {
                    editComment($(this).attr('pictureid'), $(this).attr('commentid'));
                },
            })).append($('<button>', {
                class: 'small',
                html: 'Cancel',
                commentid: commentid,
                pictureid: pictureid,
                click: function() {
                    cancelEditComment($(this).attr('pictureid'), $(this).attr('commentid'));
                },
            }));
        }
    });
}

function editComment(pictureid,commentid) {
    var params = {
        commentid: commentid,
        comment: $('#commentedit_' + commentid).val(),
    };
//    var url = '/api/editComment.jsp';
    var url = '/comment/' + commentid + '/edit/';
    $.post(url, params, function(response_html) {
        $('#comments_'+pictureid).html(response_html);
    });
}

function cancelEditComment(pictureid,commentid) {
  $('#comment_'+commentid+' .commentbuttons').fadeIn('fast');
//$('#commenttext_' + commentid + ' .comment-text')
  $('#commenttext_'+commentid + ' .comment-text').html($('#commenttext_'+commentid + ' .comment-text-hidden').html());//.slideUp('fast',function() {
//    document.getElementById('replybutton_'+commentid).onclick = function() { postReply(pictureid,commentid) };
//  });
}


function deleteComment(pictureid,commentid,artmanagerview) {
  $('#dialog_confirm_text').html("Are you sure you want to delete this comment?");
  $('#dialog_confirm').dialog({
    resizable: false,
    modal: true,
    buttons: {
      "Delete": function() {
        $(this).dialog('close');
//        var url = "/ajax_editcomment.jsp?op=delete&pictureid="+pictureid+"&commentid="+commentid;
        if (artmanagerview) {
          var url = '/ArtManager/comments/' + commentid + '/delete/';
        } else {
          var url = '/comment/' + commentid + '/delete/';
        }
        var params = {};
//        $('#commenttext_'+commentid).load(url,function() {
//          $('#commenttext_'+commentid).addClass('commentdeleted');
//        });
          $.post(url, params, function(response_html) {
              if (artmanagerview) {
console.log(response_html);
                  $('#comment_'+commentid).html(response_html);
              } else {
                  $('#comments_'+pictureid).html(response_html);
              }
          });
      },
      Cancel: function() {
        $(this).dialog('close');
      }
    }
  });
}

function deleteShout(shoutid, artmanagerview) {
  $('#dialog_confirm_text').html("Are you sure you want to delete this roar?");
  $('#dialog_confirm').dialog({
    resizable: false,
    modal: true,
    buttons: {
      "Delete": function() {
        $(this).dialog('close');
//        var url = "/ajax_shouts.jsp?op=delete&shoutid="+shoutid;
        if (artmanagerview) {
          var url = '/ArtManager/shouts/' + shoutid + '/delete/';
        } else {
          var url = '/shouts/' + shoutid + '/delete/';
        }
        params = {};
        $.post(url,params,function(data) {
            if (artmanagerview) {
                $('#shout_' + shoutid).html(data);
            } else {
                var refreshurl = '/shouts/' + data.artist_id + '/?shoutid=' + shoutid;
                $.get(refreshurl, function(html) {
                    $('#shout_' + shoutid).empty().html($(html).find('#shout_' + shoutid).children());
                });
            }
        });
      },
      Cancel: function() {
        $(this).dialog('close');
      }
    }
  });
}

function blockUser(userid,fnc,type,itemid,commentid) {
//    var url = '/api/block.jsp';
    var url = '/block/' + (userid || $('#blockuserid').val()) + '/';
    var params = {
        'blockuserid': userid || $('#blockuserid').val(),
        'fnc': fnc,
    };
    $.post(url,params,function(data) {
console.log(data);
        if (type == 'shout') {
//            var refreshurl = "/ajax_shouts.jsp?artistid="+itemid+"&offset=0&count=10";
            var refreshurl = '/shouts/' + itemid + '/?shoutid=' + commentid;
            $.get(refreshurl, function(html) {
                $('#shout_' + commentid).empty().html($(html).find('#shout_' + commentid).children());
            });
//            $('#shouts').load(refreshurl,function() {
//                Shadowbox.setup('#shouts a.button');
//            });
        } else if (type == 'comment') {
//            var refreshurl = "/ajax_comments.jsp?pictureid="+itemid;
            var refreshurl = '/comments/' + itemid + '/';
            $('#comments_'+itemid).load(refreshurl,function() {
//                Shadowbox.setup('#comments_'+itemid+' a.button');
            });
        } else if (type == 'pm') {
            if (data.success) {
                window.location.reload();
            } else {
                alert(he.decode(data.message));
            }
        } else if (type == 'direct') {
            if (data.success) {
                window.location.reload();
            } else {
                alert(he.decode(data.message));
            }
        }
    }, 'json');
}

function togglePicture(pictureid) {
  if ($('#thepicture').hasClass('preview') == true) {
    $('#thepicture').removeClass('preview');
  } else {
    $('#thepicture').addClass('preview');
  }
}

function switchFolderMode(mode,folderid,artistid) {
    if (mode == 'list') {
      $('#folderstree_list').addClass('selected');
      $('#folderstree_tree').removeClass('selected');
    } else {
      $('#folderstree_tree').addClass('selected');
      $('#folderstree_list').removeClass('selected');
    }
    getFolderTree(artistid, folderid, mode == 'list' ? true : false);
}

function sortByKey(array, key) {
    return array.sort(function(a, b) {
        var x = a[key]; var y = b[key];
        return ((x < y) ? -1 : ((x > y) ? 1 : 0));
    });
}

function foldersAtNode(folders, rootFolderId, isFlat) {
    var foldersBelowRoot = [];
    var foundRoot = false;
    var rootDepth = 0;
    if (rootFolderId == 0) {
        foldersBelowRoot = folders;
    } else {
        for (var i in folders) {
            if (folders[i].folderid == rootFolderId) {
                foundRoot = true;
                rootDepth = folders[i].depth;
            }
            if (foundRoot) {
                if (folders[i].depth <= rootDepth && folders[i].folderid != rootFolderId) {
                    foundRoot = false;
                } else {
                    folders[i].depth -= rootDepth + 1;
                    if (folders[i].folderid != rootFolderId) {
                        foldersBelowRoot.push(folders[i]);
                    }
                }
            }
        }
    }
    var result = [];
    if (isFlat) {
        result = [];
        for (var i in foldersBelowRoot) {
            if (foldersBelowRoot[i].depth == 0) {
                result.push(foldersBelowRoot[i]);
            }
        }
    } else {
        result = foldersBelowRoot;
    }
    return sortByKey(result, 'name');
}

function getFolderTree(artistid, folderid, isFlat, pruneChildren, callback) {
//    var url = '/api/folders.jsp?artistid=' + artistid;
    var url = '/folders/' + artistid;
    $.getJSON(url,function(data) {

        var roots = [];
        var sorted = [];
        var foldersKeyedById = {};

        // First make a hash of folders keyed by ID
        for (var i in data.folders) {
            var folder = data.folders[i];
            folder.children = [];
            folder.depth = 0;
            folder.numpictures_total = folder.numpictures;
            folder.newpics_total = folder.newpics;
            foldersKeyedById[folder.folderid] = data.folders[i];
        }

        // Sort folders into hierarchy of top-level roots
        for (var i in data.folders) {
            var folder = data.folders[i];
            if (folder.parent > 0 && folder.parent in foldersKeyedById) {
                var parent = foldersKeyedById[folder.parent];
                parent.children.push(folder);
            } else {
                roots.push(folder);
            }
        }

        // Create depth-aware flat list from hierarchical roots list
        while (roots.length > 0) {
            var root = roots[0];
            roots.shift();
            sorted.push(root);

            var children = root.children.sort(compare);
            for (var c in children) {
                var child = children[c];
                child.depth = root.depth + 1;
                roots.unshift(child);
            }
        }

        // Roll up numpictures counts from leaf nodes up through hierarchy
        for (var i in sorted) {
            var currentDepth = sorted[i].depth;
            for (var iterBack = i-1; iterBack >= 0; iterBack--) {
                if (sorted[iterBack].depth < currentDepth) {
                    sorted[iterBack].numpictures_total += sorted[i].numpictures;
                    sorted[iterBack].newpics_total += sorted[i].newpics;
                    currentDepth = sorted[iterBack].depth;
                }
            }
        }

        callback(sorted, foldersKeyedById, folderid, isFlat, pruneChildren);

    });
}

function displayFolders(folders, foldersKeyedById, folderid, isFlat) {
    // New block-style folder code
    $('#folders').empty();
    folderUl = $('<ul>', {
        class: 'folders',
    });

console.log(folders);
    folders = foldersAtNode(folders, folderid, isFlat);
console.log(folders);
    // Make folder objects
    for (var i in folders) {
        var folderLi = $('<li>', {
            class: 'folder',
            folderid: folders[i].folderid,
            dirname: folders[i].dirname,
            url: folders[i].url,
            click: function() {
//                window.location.href = '/Artwork/Artists/' + $(this).attr('dirname') + '/gallery/?folder_id=' + $(this).attr('folderid');
                window.location.href = $(this).attr('url');
            },
        });

        folderLi.append($('<div>', {
            class: 'foldertotal',
            html: folders[i].numpictures_total,
        }));
        folderLi.append($('<h3>', {
            class: 'foldername',
            html: folders[i].name,
        }));
        folderLi.append($('<p>', {
            class: 'folderdesc',
            html: folders[i].description,
        }));

        if (folders[i].latestpicture) {
            var latestPictureDiv = $('<div>', {
                class: 'latestpicture previewPopupTrigger',
                type: 'picture',
                itemid: folders[i].latestpicture.pictureid,
                thumbheight: folders[i].latestpicture.thumbheight,
                css: {
//                    backgroundImage: 'url(/media/Artwork/Artists/' + folders[i].dirname + '/' + folders[i].latestpicture.basename + '.p.jpg)',
                    backgroundImage: 'url(' + folders[i].latestpicture.preview_image_url + ')',
                },
            });
            folderLi.append(latestPictureDiv);
            folderLi.append($('<p>', {
                class: 'latestpicturedate',
                html: folders[i].latestpicture.uploaded + ':',
            }));
        }

        childFoldersUl = $('<ul>', {
            class: 'child-folders',
        });
        for (var c in folders[i].children) {
            var child = folders[i].children[c];
            if (c == 4 && folders[i].children.length > 5) {
                var childFolderLi = $('<li>', {
                    class: 'child-folder more-folders',
                    html: folders[i].children.length - 5 + ' more',
                });
            } else {
            var childFolderLi = $('<li>', {
                class: 'child-folder',
                title: he.decode(child.name),
                folderid: child.folderid,
                dirname: child.dirname,
                target_url: child.url,
                html: '&nbsp;',
                click: function(e) {
                    e.stopPropagation();
//                    window.location.href = '/Artists/' + $(this).attr('dirname') + '/?list=gallery&folder=' + $(this).attr('folderid');
                    window.location.href = $(this).attr('target_url');
                },
            });
            }
            childFoldersUl.append(childFolderLi);
        }
        folderLi.append(childFoldersUl);

        if (folders[i].newpics_total > 0) {
            folderLi.append($('<span>', {
                class: 'badge',
                html: folders[i].newpics_total,
            }));
        }

        folderUl.append(folderLi);
    }

    // Make breadcrumb path
    if (folderid > 0) {
        var traverseFolderId = folderid;
        var folderPath = [foldersKeyedById[traverseFolderId]];
        while (foldersKeyedById[traverseFolderId].parent) {
            traverseFolderId = foldersKeyedById[traverseFolderId].parent;
            folderPath.push(foldersKeyedById[traverseFolderId]);
        }

        var navUl = $('<ul>', {
            class: 'foldernav',
        });
        folderPath.push({
            folderid: 0,
            name: 'Main',
            noSeparator: true,
            url: '?folder_id=0',
        });
        for (var navItem in folderPath) {
            var navLi = $('<li>', {
                class: 'foldernavitem',
                html: folderPath[navItem].noSeparator ? '' : ' &raquo; ',
            });
            navLi.append($('<a>', {
                href: folderPath[navItem].url,
                html: folderPath[navItem].name,
            }));
            navUl.append(navLi);
        }
        $('.foldernav').empty().append(navUl);
    }

    $('.folders').append(folderUl);
    setupTooltipPreview();
    $(document).tooltip();
}

function displayFoldersEditable(folders, foldersKeyedById, folderid, isFlat) {
    $('#folders').empty();
    folderUl = $('<ul>', {
        class: 'folders',
    });

    for (var i in folders) {
        var folderLi = $('<li>', {
            class: 'editfolder',
            css: {
                marginLeft: folders[i].depth * 30,
            },
        });
        var folderForm = $('<form>', {
            name: 'folder_form_' + folders[i].folderid,
            id: 'folder_form_' + folders[i].folderid,
            method: 'POST',
            action: 'ArtManager.jsp',
        });
        folderForm.append($('<input>', {
            type: 'hidden',
            name: 'folderid',
            value: folders[i].folderid,
        }));
        folderForm.append($('<input>', {
            type: 'hidden',
            name: 'parent',
            value: folders[i].parent,
        }));
        folderForm.append($('<input>', {
            type: 'hidden',
            name: 'fnc',
            value: '',
        }));
        folderForm.append($('<input>', {
            type: 'hidden',
            name: 'op',
            value: 'folders',
        }));

        var folderActionsDiv = $('<div>', {
            class: 'folderactions',
        });
        folderActionsDiv.append($('<button>', {
            type: 'button',
            class: 'small',
            folderid: folders[i].folderid,
            click: function() {
                validateForm('folder_form_' + $(this).attr('folderid'), 'editFolder(' + $(this).attr('folderid') + ')');
            },
            html: 'Apply Changes',
        }));
        folderActionsDiv.append($('<button>', {
            type: 'button',
            class: 'small',
            folderid: folders[i].folderid,
            click: function() {
                globals['folderid'] = $(this).attr('folderid');
                applyFolder(document['folder_form_' + $(this).attr('folderid')], 'delete');
            },
            html: 'Delete Folder',
        }));
        folderForm.append(folderActionsDiv);

        var folderPreviewLi = $('<li>', {
            class: 'folder',
            css: {
                verticalAlign: 'top',
            },
            folderid: folders[i].folderid,
            click: function() {
//                window.location.href = '/ArtManager.jsp?op=artwork&folderid=' + $(this).attr('folderid');
                window.location.href = '/ArtManager/artwork/?folderid=' + $(this).attr('folderid');
            },
        });
        folderPreviewLi.append($('<div>', {
            class: 'foldertotal',
            html: folders[i].numpictures,
        }));
        folderPreviewLi.append($('<h3>', {
            class: 'foldername',
            html: folders[i].name,
        }));
        folderPreviewLi.append($('<p>', {
            class: 'folderdesc',
            html: folders[i].description,
        }));

        if (folders[i].latestpicture) {
            folderPreviewLi.append($('<div>', {
                class: 'latestpicture previewPopupTrigger',
                type: 'picture',
                itemid: folders[i].latestpicture.pictureid,
                thumbheight: folders[i].latestpicture.thumbheight,
                css: {
//                    backgroundImage: 'url(/Artwork/Artists/' + folders[i].dirname + '/' + folders[i].latestpicture.basename + '.p.jpg)',
                    backgroundImage: 'url(' + folders[i].latestpicture.preview_image_url + ')',
                },
            }));
            folderPreviewLi.append($('<p>', {
                class: 'latestpicturedate',
                html: folders[i].latestpicture.uploaded + ':',
            }));
        }

        folderForm.append(folderPreviewLi);

        var folderFormTable = $('<table>', {
            class: 'formtable',
            css: {
                display: 'inline-block',
                width: 400,
                paddingTop: 30,
            },
        });

        var folderFormTableTrName = $('<tr>');
        var folderFormTableTdNameLabel = $('<td>', {
            class: 'label',
            html: 'Name',
        });
        folderFormTableTdName = $('<td>');
        folderFormTableTdName.append($('<input>', {
            type: 'text',
            name: 'name',
            id: 'name_' + folders[i].folderid,
            value: folders[i].name,
            maxlength: 64,
            validate: 'hasvalue',
            message: 'The folder name cannot be blank.',
        }));
        folderFormTableTrName.append(folderFormTableTdNameLabel);
        folderFormTableTrName.append(folderFormTableTdName);

        var folderFormTableTrDescription = $('<tr>');
        var folderFormTableTdDescriptionLabel = $('<td>', {
            class: 'label',
            html: 'Description',
        });
        folderFormTableTdDescriptionLabel.append($('<div>', {
            class: 'charcount',
            id: 'descr_' + folders[i].folderid + '_charcount',
            html: folders[i].description.length + ' / 255',
        }));
        var folderFormTableTdDescription = $('<td>');
        folderFormTableTdDescription.append($('<textarea>', {
            name: 'description',
            id: 'description_' + folders[i].folderid,
            validate: 'maxlen:255',
            message: 'The description is too long.',
            html: folders[i].description,
            folderid: folders[i].folderid,
            keyup: function() {
                refreshCharCount(this, 255, 'descr_' + $(this).attr('folderid') + '_charcount');
            },
        }));
        folderFormTableTrDescription.append(folderFormTableTdDescriptionLabel);
        folderFormTableTrDescription.append(folderFormTableTdDescription);

        var folderFormTableTrMoveTo = $('<tr>');
        var folderFormTableTdMoveToLabel = $('<td>', {
            class: 'label',
            html: 'Move to',
        });
        var folderFormTableTdMoveTo = $('<td>');
        var folderFormTableTdMoveToSelect = $('<select>', {
            name: 'parent',
            id: 'parent_' + folders[i].folderid,
            class: 'foldermenu no-autoload',
        });
        folderFormTableTdMoveToSelect.append($('<option>', {
            value: 0,
            html: '(Main)',
        }));

        var foundNode = false;
        var nodeDepth = 0;
        for (var f in folders) {
            if (foundNode && folders[f].depth <= nodeDepth) {
                foundNode = false;
            }
            if (folders[f].folderid == folders[i].folderid) {
                foundNode = true;
                nodeDepth = folders[f].depth;
            }
            if (!foundNode) {
                folderFormTableTdMoveToSelect.append($('<option>', {
                    value: folders[f].folderid,
                    html: Array(folders[f].depth + 2).join('&nbsp;&nbsp;&nbsp;') + folders[f].name,
                    selected: folders[f].folderid == folders[i].parent,
                }));
            }
        }

        folderFormTableTdMoveTo.append(folderFormTableTdMoveToSelect);
        folderFormTableTrMoveTo.append(folderFormTableTdMoveToLabel);
        folderFormTableTrMoveTo.append(folderFormTableTdMoveTo);

        folderFormTable.append(folderFormTableTrName);
        folderFormTable.append(folderFormTableTrDescription);
        folderFormTable.append(folderFormTableTrMoveTo);

        folderForm.append(folderFormTable);

        folderLi.append(folderForm);

        folderUl.append(folderLi);
    }
    $('#folders_edit').append(folderUl);
    setupTooltipPreview();
}

function getFolderSelect(folders, foldersKeyedById, folderid, isFlat, pruneChildren) {
    $('select.foldermenu').not('.no-autoload').each(function() {
        for (var i in folders) {
            $(this).append($('<option>', {
                value: folders[i].folderid,
                html: Array(folders[i].depth + 2).join('&nbsp;&nbsp;&nbsp;') + folders[i].name,
                selected: folders[i].folderid == parseInt($(this).attr('folderid'))
            }));
        }
    });
}

function createFolder() {
//    var url = '/api/createFolder.jsp';
    var url = '/ArtManager/folders/create/';
    var params = {
        name: $('#name_new').val(),
        parent: $('#parent_new').val(),
    };
console.log(params);
    $.post(url, params, function(data) {
        if (data.success) {
            window.location.reload();
        } else {
            alert(data.message);
        }
    }, 'json');
}

function editFolder(folderid) {
//    var url = '/api/editFolder.jsp';
    var url = '/ArtManager/folders/' + folderid + '/update/';
    var params = {
        folderid: folderid,
        name: $('#name_' + folderid).val(),
        description: $('#description_' + folderid).val(),
        parent: $('#parent_' + folderid).val(),
    };
    $.post(url, params, function(data) {
        if (data.success) {
            window.location.reload();
        } else {
            alert(data.message);
        }
    }, 'json');
}

function deleteFolder(folderid) {
//    var url = '/api/deleteFolder.jsp';
    var url = '/ArtManager/folders/' + folderid + '/delete/';
    var params = {
        folderid: folderid,
        parent: $('#parent_' + folderid).val(),
    };
    $.post(url, params, function(data) {
        if (data.success) {
            window.location.reload();
        } else {
            alert(data.message);
        }
    }, 'json');
}

function updatePrefs(fnc) {
    var url = $('#artistform').attr('action');
    var params = {
        fnc: fnc,
        username: $('#newname').val(),
        sort_name: $('#sortname').val(),
        password: $('#password').val(),
        password_repeat: $('#password_repeat').val(),
        is_public: $('#is_public').val() == '1',
        email: $('#email').val(),
        show_email: $('#showemail').prop('checked'),
        description: $('#artistdesc').val(),
        commissions_open: $('#commissions').prop('checked'),
        birth_date: $('#birthdate_pick').val(),
        show_birthdate: $('#showbirthdate').prop('checked'),
        show_birthdate_age: $('#showbirthdate_age').prop('checked'),
        gender: $('#gender').val(),
        pronouns: $('#pronouns').val(),
        location: $('#location').val(),
        occupation: $('#occupation').val(),
        website: $('#website').val(),
        timezone: $('#timezone').val(),
        allow_shouts: $('#allowshouts').prop('checked'),
        allow_comments: $('#allowcomments').prop('checked'),
        email_shouts: $('#emailshouts').prop('checked'),
        email_comments: $('#emailcomments').prop('checked'),
        email_pms: $('#emailpms').prop('checked'),
        show_coloring_cave: $('#showcc').prop('checked'),
        tooltips_enabled: $('#tooltips_enabled').prop('checked'),
    };
console.log(params);
    $.post(url, params, function(data) {
console.log(data);
        if (data.success) {
//            if (data.name_changed || data.passwd_changed) {
//                set_prefsname(data.storename, data.storepass);
//            }
            window.location.reload();
        } else {
            errorText = '';
            Object.keys(data.errors).forEach(function(key) {
                errorText += data.errors[key][0] + '\n';
                console.log(key, data.errors[key][0]);
            });
            alert(errorText);
        }
    }, 'json');
}

function listArtists(list, count) {
    let url = `/artists/list/${list}/`;
    const params = [];
    if ((list === 'search' || list === 'tag') && count > 0) {
        params.push({name: 'term', value: encodeURIComponent($('#searchtext').val())});
    }
    const queryParts = [];
    params.forEach(function(e){
        queryParts.push(e.name + '=' + e.value);
    });
    const queryPartsWithCount = queryParts.slice();
    queryPartsWithCount.push('count=' + count);
    let queryStr = queryPartsWithCount.join('&');
    url += `?${queryStr}`;
    $('.spinner').show();
    $('#artists').slideUp('fast',function() {
        $('#artists').load(url,function() {
            $('.spinner').hide();
            setupTooltipPreview();
            $('#artists').slideDown('fast');
            artistlistopen = list;
            $('h2.itemlist').removeClass('itemlist_selected');
            $('#artistlisth2_'+list).addClass('itemlist_selected');
            if (typeof(window.history.replaceState) !== "undefined") {
                queryStr = queryParts.join('&');
                window.history.replaceState('', '', '/Artists/' + list + '/' + (queryStr ? '?' : '') + queryStr);
            }
        });
    });
}

function listArtwork(list, count) {
    let url = `/artwork/list/${list}/`;
    const params = [];
    if ((list === 'search' || list === 'tag') && count > 0) {
        params.push({name: 'term', value: encodeURIComponent($('#searchtext').val())});
        params.push({name: 'year_from', value: $('#id_year_from').val()});
        params.push({name: 'year_to', value: $('#id_year_to').val()});
    }
    const queryParts = [];
    params.forEach(function(e){
        queryParts.push(e.name + '=' + e.value);
    });
    const queryPartsWithCount = queryParts.slice();
    queryPartsWithCount.push('count=' + count);
    let queryStr = queryPartsWithCount.join('&');
    url += `?${queryStr}`;
    $('.spinner').show();
    $('#artwork').slideUp('fast', function() {
        $('#artwork').load(url, function() {
            $('.spinner').hide();
            setupTooltipPreview();
            $('#artwork').slideDown('fast');
            artworklistopen = list;
            $('h2.itemlist').removeClass('itemlist_selected');
            $(`#artworklisth2_${list}`).addClass('itemlist_selected');
            if (typeof(window.history.replaceState) !== "undefined") {
                queryStr = queryParts.join('&');
                window.history.replaceState('', '', `/Artwork/${list}/` + (queryStr ? '?' : '') + queryStr);
            }
        });
    });
}

function listCharacters(list, count) {
    console.log('listCharacters');
    let url = `/characters/list/${list}/`;
    const params = [];
    if ((list === 'search' || list === 'tag') && count > 0) {
        params.push({name: 'term', value: encodeURIComponent($('#searchtext').val())});
    }
    const queryParts = [];
    params.forEach(function(e){
        queryParts.push(e.name + '=' + e.value);
    });
    const queryPartsWithCount = queryParts.slice();
    queryPartsWithCount.push('count=' + count);
    let queryStr = queryPartsWithCount.join('&');
    url += `?${queryStr}`;
    console.log(url);
    $('.spinner').show();
    $('#characters').slideUp('fast',function() {
        $('#characters').load(url,function() {
            $('.spinner').hide();
            setupTooltipPreview();
            $('#characters').slideDown('fast');
            characterslistopen = list;
            $('h2.itemlist').removeClass('itemlist_selected');
            $('#characterslisth2_'+list).addClass('itemlist_selected');
            if (typeof(window.history.replaceState) !== "undefined") {
                queryStr = queryParts.join('&');
                window.history.replaceState('', '', '/Characters/' + list + '/' + (queryStr ? '?' : '') + queryStr);
            }
            console.log(list);
            if (list == 'search') {
                setupAutocompleteArtist($('input#artist_pick_search'),"updateCharacterList('artist',ui.item.artistid,1);");
                setupAutocompleteSpecies('search',"updateCharacterList('species',ui.item.species,1);");
                setupAutocompleteCharacter('search',"updateCharacterList('charactername',ui.item.name,1);");
                let speciesUrl = '/characters/species/';
                console.log(speciesUrl);
                console.log($('#species_list'));
                $('.spinner').clone().appendTo($('#species_list')).show();
                $('#species_list').load(speciesUrl, function() {
                    $('#species_list .spinner').hide();
                    setupTooltipPreview();
                });
            }
        });
    });
}

function getMoreArtists(start, list, count, term, moreButtonSelector) {
//  var url = "/ajax_listartists.jsp?start="+start+"&list="+list+"&count="+count+"&term="+term;
//   var url = '/artists/' + list + '/?start=' + start + '&count=' + count + '&term=' + term;
  var url = `/artists/list/${list}/?start=${start}&count=${count}&term=${term}`;
    $('.spinner').show();
  $.ajax({ url: url, success: function(data) {
    $('.spinner').hide();
//    $('#artists_'+list).append(data);
    let moreButtons = document.querySelectorAll(moreButtonSelector);
    for (const s of moreButtons) {
        s.style.display = "none";
    }
    $('#artists').append(data);
//    Shadowbox.setup('td.thumb a,a.profilelink');
    setupTooltipPreview();
    if (typeof(window.history.replaceState) !== "undefined") {
      var termstr = '';
      if (term != '') {
        termstr = "&term="+term;
      }
      window.history.replaceState('', '', '/Artists/' + list + '/?start=' + start + termstr);
    }
  }});
  ArtistList[list] = start;
}

function getMoreArtwork(start, list, count, term, yearFrom, yearTo, moreButtonSelector) {
//  var url = "/ajax_listartwork.jsp?start="+start+"&list="+list+"&count="+count+"&term="+term;
  var url = `/artwork/list/${list}/?start=${start}&count=${count}&term=${term}&year_from=${yearFrom}&year_to=${yearTo}`;
    let moreButtons = document.querySelectorAll(moreButtonSelector);
    for (const s of moreButtons) {
        s.classList.add('loading-spinner');
    }
    $('.spinner').show();
  $.ajax({ url: url, success: function(data) {
    $('.spinner').hide();
//    $('#artwork_'+list).append(data);
    for (const s of moreButtons) {
        s.style.display = "none";
    }
    $('#artwork').append(data);
//    Shadowbox.setup('td.thumb a');
//     obj.style.display='none';
    setupTooltipPreview();
    if (typeof(window.history.replaceState) !== "undefined") {
      var termstr = '';
      if (term != '') {
        termstr = "&term="+term;
      }
      window.history.replaceState('', '', '/Artwork/' + list + '/?start=' + start + termstr);
    }
  }});
  ArtworkList[list] = start;
}

function getMoreCharacters(start, list, subList, count, term, moreButtonSelector, dirName, matchType) {
//  var url = "/ajax_listartwork.jsp?start="+start+"&list="+list+"&count="+count+"&term="+term;
  var url = `/characters/list/${list}/?start=${start}&count=${count}&list=${subList}&term=${term}&dir_name=${dirName}&match=${matchType}`;
    let moreButtons = document.querySelectorAll(moreButtonSelector);
    for (const s of moreButtons) {
        s.classList.add('loading-spinner');
    }
    $('.spinner').show();
  $.ajax({ url: url, success: function(data) {
    $('.spinner').hide();
//    $('#artwork_'+list).append(data);
    for (const s of moreButtons) {
        s.style.display = "none";
    }
    $('#characters').append(data);
//    Shadowbox.setup('td.thumb a');
//     obj.style.display='none';
    setupTooltipPreview();
    if (typeof(window.history.replaceState) !== "undefined") {
      var termstr = '';
      if (term != '') {
        termstr = "&term="+term;
      }
      if (dirName != '') {
        termstr += "&dir_name="+dirName;
      }
      window.history.replaceState('', '', '/Characters/' + list + '/?start=' + start + termstr);
    }
  }});
  CharactersList[list] = start;
}

function doSearch(mode) {

}

function setupRecovery(recovertype) {
//  var url = "/ajax_recover.jsp?type="+recovertype;
//  $('#recovery').load(url,function() {
//    setupAutocompleteArtist('recover');
//  });
    $('#recovery').hide();
    $('#recovery_' + recovertype).show();
}

function votePicture(contestid,entryid) {
//  document.contestform.pictureid.value=pictureid;
  document.contestform.entry.value=entryid;
  document.contestform.submit();
}

function removeContestPic(entryid) {
  $('#dialog_confirm_text').html("Are you sure you want to remove this picture from the contest?");
  $('#dialog_confirm').dialog({
    resizable: false,
    modal: true,
    buttons: {
      "Remove": function() {
        var url = '/contest/entry/' + entryid + '/delete/';
        $.post(url, {}, function(data) {
          window.location.reload();
        });
//        selform.pictureid.value=pictureid;
//        selform.fnc.value='removepicture';
//        selform.submit();
      },
      Cancel: function() {
        $(this).dialog('close');
      }
    }
  });
}

function createContest() {
    var url = '/ArtManager/contests/create/';
    var params = {
        title: $('#title_new').val(),
        description: $('#description_new').val(),
        rules: $('#rules_new').val(),
        date_end: $('#deadline_pick_new').val(),
        allow_voting: $('#allow_voting_new').prop('checked'),
    };
    $.post(url, params, function(data) {
        if (data.success) {
            window.location.reload();
        }
    });
}

function applyContest(selform,contestid,fnc) {
  var c = false;
  var params = {};
  if (fnc == 'delete') {
    $('#dialog_confirm_text').html("Are you sure you want to delete this contest?");
    c = true;
  } else if (fnc == 'cancel') {
    $('#dialog_confirm_text').html("Are you sure you want to cancel and delete this contest?");
    c = true;
    params = {
      is_active: false,
      is_cancelled: true,
    };
  } else if (fnc == 'publish') {
    $('#dialog_confirm_text').html("Are you sure you are ready to publish this contest?");
    c = true;
    params = {
      is_active: true,
    };
  } else if (fnc == 'unpublish') {
    $('#dialog_confirm_text').html("Are you sure you want to unpublish this contest?");
    c = true;
    params = {
      is_active: false,
    };
  } else if (fnc == 'update') {
    params = {
        title: $('#title_' + contestid).val(),
        description: $('#description_' + contestid).val(),
        rules: $('#rules_' + contestid).val(),
        date_end: $('#deadline_pick_' + contestid).val(),
        allow_voting: $('#allowvoting_' + contestid).prop('checked'),
    };
    updateContest(contestid, fnc, params);
  }
  if (c) {
    $('#dialog_confirm').dialog({
      resizable: false,
      modal: true,
      buttons: {
        "OK": function() {
          updateContest(contestid, fnc, params);
        },
        Cancel: function() {
          $(this).dialog('close');
        }
      }
    });
  }
}

function updateContest(contestid, fnc, params) {
    var url = '/ArtManager/contests/' + contestid + '/' + fnc + '/';
    $.post(url, params, function(data) {
        if (data.success) {
            window.location.reload();
        }
    });
}

function showContestEntries(contestid) {
    var url = '/ArtManager/contests/' + contestid + '/entries/';
    $('#contest_entries_' + contestid).load(url);
}

function newPM(recipient_id, query_str) {
    var url = '/pm/user/';
    if (recipient_id) {
        url += recipient_id + '/';
    }
    url += '?' + query_str;
console.log(url);
    $('#pms').load(url, function(data) {
        setupAutocompleteArtist($('input#recpt'), 'validatePMRecipient()');
    });
}

function validatePMRecipient() {
    var recpt_name = $('input#recpt').val();
    if (recpt_name) {
        var url = '/artists-ac/' + recpt_name + '/';
        $.getJSON(url, function(data) {
            if (data.artists.length == 0) {
                $('#recipient_error').html('Recipient not found. Please use the autocomplete drop-down to select a recipient.').show();
                $('#recpt').addClass('error');
                $('#recipient').val('');
            } else if (data.artists[0].userid == parseInt($('#sender').val())) {
                $('#recipient_error').html('You cannot send a Private Message to yourself.').show();
                $('#recpt').addClass('error');
                $('#recipient').val('');
            } else {
                $('#recipient_error').hide();
                $('#recpt').removeClass('error');
                $('#recipient').val(data.artists[0].userid);
            }
        });
    }
}

function showBulletin(bulletin_id) {
    var url = '/bulletin/' + bulletin_id;
    $('#dialog_bulletin').load(url, function() {
        $('#dialog_bulletin').dialog('open');
    });
/*
    Shadowbox.open({
        player: 'iframe',
        content: url,
        width: 500,
        height: 600
    });
*/
}

function showPM(pm_id) {
    var url = '/ArtManager/private_msgs/' + pm_id + '/';
    window.location.href = url;
}

function showPMReply() {
    $('#show_pm_reply').fadeOut(10, function() {
        $('#pm_reply').slideDown(100, function() {});
    });
}

function hidePMReply() {
    $('#pm_reply').slideUp(100, function() {
        $('#show_pm_reply').show();
    });
}

function refreshPMBox(pmbox,page,viewmode,showpages,showstatus,w) {
  if (!w) {
    w = window;
  }
  var S = w.Shadowbox;
//  var url = "ajax_pms.jsp?op=privatemsgs&page="+page+"&box="+pmbox+"&viewmode="+viewmode+"&showpages="+showpages+"&showstatus="+showstatus;
  var url = '/pms/' + pmbox + '/?op=privatemsgs&page='+page+"&box="+pmbox+"&viewmode="+viewmode+"&showpages="+showpages+"&showstatus="+showstatus;
  $('#pms',w.document).load(url,function() {
//    S.setup('#pms table a');
    $('div.selector a',w.document).removeClass('selected');
    $('div.selector a#sel_'+pmbox,w.document).addClass('selected');
    $('.pms tr.pm-row td.clickable').click(function() {
        showPM($(this).attr('pm_id'));
    });
  });
}

function turnPage(page,queryStr) {
  var qsParam = [];
  var params = queryStr.split('&');
  for (var i=0; i<params.length; i++) {
    var pos = params[i].indexOf('=');
    if (pos > 0) {
      var key = params[i].substring(0,pos);
      var val = params[i].substring(pos+1);
      qsParam[key] = val;
    }
  }
  if (qsParam['op'] == 'privatemsgs' || qsParam['op'] == 'dashboard') {
    refreshPMBox(qsParam['box'],page,qsParam['viewmode'],1,1);
  }
}

function refreshSketcherLogin() {
  var url = "/Sketcher/ajax_sketcher.jsp";
  $('#sketcher').load(url);
}

function refreshSketcherUserBox() {
    const url = '/userbox/sketcher_box/';
    $('#sketcher_box').load(url, function(html) {
        const $html = $(html);
        const sketcherUsers = $html.contents('.sketcheruser .sketcher-user-name').length;
        $('.sketcher-users-count').html(sketcherUsers);
        if (sketcherUsers === 1) {
            $('.sketcher-users-count-label').html('user');
        } else {
            $('.sketcher-users-count-label').html('users');
        }
    });
}

function refreshResetStatus() {  
  var url = "/Sketcher/ajax_resetstatus.jsp";   
  $('#resetstatus').load(url);
}

function connectSketcher() {
//  var url = "/Sketcher/ajax_sketcher.jsp?login=true&sounds="+$('#sounds').attr('checked');
//  clearInterval(sketcherIntvl);
//  $('#sketcher').load(url);
  var name = "Sketcher";
  var width = screen.width;
  var height = screen.height;
  var url = "/Sketcher/Sketcher.jsp?h=" + height + "&sounds=" + ($('#sounds').prop('checked') ? 1 : 0);
  var settings = 
  "toolbar=no,location=no,directories=no,"+
  "status=no,menubar=no,scrollbars=yes,"+
  "resizable=yes,width="+width+",height="+height;
  MyNewWindow=window.open(url,name,settings);
  MyNewWindow.resizeTo(width,height);
  return false;
}

var jumpToHash = function (hash) {
    var sectionPos;
    targetElem = $(hash);
    sectionPos = targetElem.offset().top;
    if (sectionPos) {
        $('html, body').animate({
            scrollTop: sectionPos
        }, 500);
    }
};

$(document).ready(function() {
  $("input#artistlogin,input#recpt,input#blockuser,input#searchartist").autocomplete({
    source: function(request, response) {
      $.ajax({
//        url: "/ajax_ac_artists.jsp",
        url: '/artists-ac/' + request.term,
        dataType: "json",
        data: {
          term: request.term
        },
        success: function(data) {
          response($.map(data.artists, function(item) {
            return {
              label: he.decode(item.name),
              value: he.decode(item.name),
              artistid: item.artistid,
              userid: item.userid,
              dirname: item.dirname,
            }
          }))
        },
      })
    },
    select: function(e, ui) {
      if ($(this).attr('id') == "searchartist") {
        window.location.href = '/Artists/' + ui.item.dirname;
      }
      if ($(this).attr('id') == 'blockuser') {
        $('#blockuserid').val(ui.item.userid);
      }
      if ($(this).attr('id') == 'recpt') {
        $('#recipient').val(ui.item.userid);
      }
    },
  });
  setupAutocompleteArtist($('input#artist_pick_search'),"updateCharacterList('artist',ui.item.artistid,1);");
  setupAutocompleteSpecies('search',"updateCharacterList('species',ui.item.species,1);");
  setupAutocompleteCharacter('search',"updateCharacterList('charactername',ui.item.name,1);");

  setupAutocompleteCharacter('add',"filterCharacter(ui.item.characterid,'add');");

  $('#offerslayout,div.masonry').masonry({ singleMode: false, animate: true });
//  $('#favoritepicturesbox').masonry({ singleMode: true });
  $('#birthdate_pick').datepicker();
//  $('#birthdate_pick').datepicker("option", "dateFormat", "m/d/yy");
  $('#birthdate_pick').datepicker("option", "dateFormat", "yy-mm-dd");
  $('#birthdate_pick').datepicker("option", "changeYear", true);
  $('#birthdate_pick').datepicker("option", "defaultDate", "-14y");
//  $('.picturetile a').wTooltip({
//    ajax: "/ajax_tooltip_picture.jsp"
//  });
  $('.actions_menu a').mouseenter(function() {
    $(this).addClass('ui-state-hover');
  });
  $('.actions_menu a').mouseleave(function() {
    $(this).removeClass('ui-state-hover');
  });
  var sketcherboxIntv = setInterval('refreshSketcherUserBox()',sketcherboxIntvMs);
  $('#keywords_new').tagsInput({
    'height': '50px',
    'defaultText': 'add new'
  });
  Shadowbox.init({
//    skipSetup: true
//    flashParams: {bgcolor: "#ffffff",wmode: "opaque"},
    fadeDuration: 0.1,
    resizeDuration: 0.1,
    flashParams: {wmode: "opaque"},
    onFinish: function() {
      $('#sb-body-inner img').one('click',function() {
        var pictureid = this.src.split('?')[1];
        if (pictureid) {
          Shadowbox.close();
//          window.parent.location.href='/Picture.jsp?pictureid=' + pictureid;
          window.parent.location.href='/picture/' + pictureid;
        }
      });
    }
  });

    getMoreBulletins(0, globals.bulletinsToLoad);
    getMoreAdminAnnouncements(0, globals.adminAnnouncementsToLoad);
    $('.bulletinsinner').scroll(function(e) {
        const bottomMargin = $(this)[0].scrollHeight - $(this).scrollTop() - globals.scrollBottomMargin;
        if (bottomMargin < $(this).outerHeight()) {
            if ($(this).attr('bulletin_type') === 'admin_announcements') {
                getMoreAdminAnnouncements(globals.adminAnnouncementsCount, globals.adminAnnouncementsToLoad);
            } else {
                getMoreBulletins(globals.bulletinsCount, globals.bulletinsToLoad);
            }
        }
    });

    const shoutsContainer = $('.shouts-container');
    if (shoutsContainer.length) {
        getMoreShouts(shoutsContainer.attr('artistid'), 0, globals.shoutsToLoad);
        shoutsContainer.scroll(function(e) {
            const bottomMargin = $(this)[0].scrollHeight - $(this).scrollTop() - globals.scrollBottomMargin;
            if (bottomMargin < $(this).outerHeight()) {
                getMoreShouts(shoutsContainer.attr('artistid'), globals.shoutsCount, globals.shoutsToLoad);
            }
        });
    }

  $('.tooltip').tooltip();
  setupTooltipPreview();

    $('#dialog_bulletin').dialog({
//      title: 'Bulletin',
      resizable: false,
      modal: true,
      autoOpen: false,
      width: '70%',
      maxHeight: 600,
      dialogClass: 'no-titlebar',
      buttons: {
        "Close": function() {
          $(this).dialog('close');
        }
      }
    });

    if ($('#folders').length > 0) {
        getFolderTree($('#folders').attr('artistid'), $('#folders').attr('folderid'), true, false, displayFolders);
    }
    if ($('#folders_edit').length > 0) {
        getFolderTree($('#folders_edit').attr('artistid'), $('#folders_edit').attr('folderid'), true, false, displayFoldersEditable);
    }
    if ($('select.foldermenu').length > 0 && $('#edit_artistid').length) {
        getFolderTree($('#edit_artistid').val(), null, true, false, getFolderSelect);
    }

    $('.random-popular').load('/random_popular/', function() {
        setupTooltipPreview();
    });

});
