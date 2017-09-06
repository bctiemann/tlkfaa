<!-- Original:  Bill Dortch, Idaho Design (bdortch\@netw.com)

<!-- This script and many more are available free online at -->
<!-- The JavaScript Source!! http://javascript.internet.com -->

var expdays = 90;

<!-- Begin
function getCookieVal (offset) {
  var endstr = document.cookie.indexOf (";", offset);
  if (endstr == -1)
    endstr = document.cookie.length;
  return unescape(document.cookie.substring(offset, endstr));
}
function GetCookie (name) {
  var arg = name + "=";
  var alen = arg.length;
  var clen = document.cookie.length;
  var i = 0;
  while (i < clen) {
    var j = i + alen;
    if (document.cookie.substring(i, j) == arg)
      return getCookieVal (j);
    i = document.cookie.indexOf(" ", i) + 1;
    if (i == 0) break; 
  }
  return null;
}  
 function SetCookie (name, value) {
  var argv = SetCookie.arguments;
  var argc = SetCookie.arguments.length;
  var expires = (argc > 2) ? argv[2] : null;
  var path = (argc > 3) ? argv[3] : null;
  var domain = (argc > 4) ? argv[4] : null;
  var secure = (argc > 5) ? argv[5] : false;
  document.cookie = name + "=" + encodeURIComponent(value) +
    ((expires == null) ? "" : ("; expires=" + expires.toGMTString())) +
    ((path == null) ? "" : ("; path=" + path)) +
    ((domain == null) ? "" : ("; domain=" + domain)) +
    ((secure == true) ? "; secure" : "");
}
function DeleteCookie (name) {
  var argv = DeleteCookie.arguments;
  var argc = DeleteCookie.arguments.length;
  var path = (argc > 1) ? argv[1] : null;
  var domain = (argc > 2) ? argv[2] : null;
  if (GetCookie(name)) {
     document.cookie = name + "=" +
      ((path) ? "; path=" + path : "") +
      ((domain) ? "; domain=" + domain : "") +
      "; expires=Thu, 01-Jan-70 00:00:01 GMT";
  }
}
function set_name(artistname,artistpasswd) {
  var expdate = new Date ();
  expdate.setTime (expdate.getTime() + (24 * 60 * 60 * 1000 * expdays));
  if (artistname != "") {
    SetCookie ("artistname", artistname, expdate, "/");
    SetCookie ("artistpasswd", artistpasswd, expdate, "/");
  }
}
function set_prefsname(prefsname,prefspasswd) {
  var expdate = new Date ();
  expdate.setTime (expdate.getTime() + (24 * 60 * 60 * 1000 * expdays));
  if (prefsname != "")
    SetCookie ("prefsname", prefsname, expdate, "/");
  if (prefspasswd != "")
    SetCookie ("prefspasswd", prefspasswd, expdate, "/");
}
function set_view(viewStr) {
  var expdate = new Date ();
  expdate.setTime (expdate.getTime() + (24 * 60 * 60 * 1000 * expdays));
  SetCookie ("view", viewStr, expdate, "/");
}
function set_bulletins(showBulletins) {
  var expdate = new Date ();
  expdate.setTime (expdate.getTime() + (24 * 60 * 60 * 1000 * expdays));
  SetCookie ("showbulletins", showBulletins, expdate, "/");
}
function set_folders(folderViewMode) {
  var expdate = new Date ();
  expdate.setTime (expdate.getTime() + (24 * 60 * 60 * 1000 * expdays));
  SetCookie ("folderview", folderViewMode, expdate, "/");
}
function set_tzoffset() {
  var expdate = new Date ();
  var localclock = new Date();
  var tzRaw = localclock.getTimezoneOffset() * 60;
  expdate.setTime (expdate.getTime() + (24 * 60 * 60 * 1000 * expdays));
  SetCookie ("tzoffset", tzRaw, expdate, "/");
}
function doLogin() {
//  set_prefsname(document.prefslogin.userlogin.value,document.prefslogin.userpasswd.value);
  var passwd = document.loginform.artistpasswd.value;
  var passwdhash = hex_md5(passwd);
  set_prefsname(document.loginform.artistlogin.value,passwdhash);
  window.location.reload();
  return false;
}
function doLogout() {
  DeleteCookie("prefsname","/");
  DeleteCookie("prefspasswd","/");
// This should push to the front page
//  window.location.reload();
  window.location = "/";
}
// End -->
