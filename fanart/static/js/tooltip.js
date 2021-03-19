window.viewport =
{
    height: function() {
        return $(window).height();
    },

    width: function() {
        return $(window).width();
    },

    scrollTop: function() {
        return $(window).scrollTop();
    },

    scrollLeft: function() {
        return $(window).scrollLeft();
    }
};

var setupTooltipPreview = function() {
  var hideDelay = 500;
  var currentID;
  var hideTimer = null;

  xOffset = 10;
  yOffset = 20;
  fadeInTime = 300;

  $('#previewPopupContainer').remove();

  // One instance that's reused to show info for the current person
  var container = $('<div id="previewPopupContainer"><div id="previewPopupContent"></div></div>');
/*
      + '<table width="" border="0" cellspacing="0" cellpadding="0" align="center" class="previewPopupPopup">'
      + '<tr>'
      + '   <td class="corner topLeft"></td>'
      + '   <td class="top"></td>'
      + '   <td class="corner topRight"></td>'
      + '</tr>'
      + '<tr>'
      + '   <td class="left">&nbsp;</td>'
      + '   <td><div id="previewPopupContent"></div></td>'
      + '   <td class="right">&nbsp;</td>'
      + '</tr>'
      + '<tr>'
      + '   <td class="corner bottomLeft">&nbsp;</td>'
      + '   <td class="bottom">&nbsp;</td>'
      + '   <td class="corner bottomRight"></td>'
      + '</tr>'
      + '</table>'
      + '</div>');
*/

  $('body').append(container);

  $('.previewPopupTrigger').off('mouseover');
  $('.previewPopupTrigger').on('mouseover', function(e)
  {

      if (!tooltips_enabled) {
        return;
      }

      // format of 'rel' tag: type,id
//      var settings = $(this).attr('rel').split(',');
//      var type = settings[0];
//      var id = settings[1];
      var type = $(this).attr('type');
      var id = $(this).attr('itemid');


      // If no guid in url rel tag, don't popup blank
      if (currentID == '')
          return;

      if (hideTimer)
          clearTimeout(hideTimer);

      var pos = $(this).offset();
      var width = $(this).width();

/*
      var mousex = e.pageX + 20;
      var mousey = e.pageY + 20;
      var tipWidth = $('#previewPopupContainer').width();
      var tipHeight = $('#previewPopupContainer').height();

      var tipVisX = $(window).width() - (mousex + tipWidth);
      var tipVisY = $(window).height() - (mousey + tipHeight);

      if ( tipVisX < 20 ) { //If tooltip exceeds the X coordinate of viewport
        mousex = e.pageX - tipWidth - 20;
      } if ( tipVisY < 20 ) { //If tooltip exceeds the Y coordinate of viewport
        mousey = e.pageY - tipHeight - 20;
      }

      container.css({
//          left: (pos.left + width) + 'px',
//          top: pos.top - 5 + 'px'
        left: mousex,
        top: mousey
      });
*/

      $('#previewPopupContent').html('&nbsp;');

//      var popuptype = {
//          'picture': 'picture',
//          'coloring_picture': 'coloring_picture',
//      }
      var popuptype;
      if (type == 'picture' || type == 'ccpic') {
        popuptype = "picture";
      } else if (type == 'character') {
        popuptype = "character";
      } else if (type == 'msg') {
        popuptype = "text";
      } else if (type == 'bannedartist') {
        popuptype = "bannedartist";
      }

      $.ajax({
          type: 'GET',
          url: '/tooltip/' + type + '/' + id + '/',
          success: function(data)
          {
              // Verify that we're pointed to a page that returned the expected results.
              if (data.indexOf('previewPopupResult') < 0)
              {
                  $('#previewPopupContent').html('<span >Error</span>');
//                  $('#previewPopupContent').html('<span >Page ' + id + ' did not return a valid result for person ' + id + '.
//Please have your administrator check the error log.</span>');
              }

              // Verify requested person is this person since we could have multiple ajax
              // requests out if the server is taking a while.
              if (data.indexOf(id) > 0)
              {
                  $('#previewPopupContent').html(data);
                  positionToolTip(e,this);
                  container.css('display', 'block');
              }
          }
      });

  });

  $('.previewPopupTrigger').off('mouseout');
  $('.previewPopupTrigger').on('mouseout', function()
  {
      if (hideTimer)
          clearTimeout(hideTimer);
      hideTimer = setTimeout(function()
      {
          container.css('display', 'none');
      }, hideDelay);
  }).on('click', function() {
      container.css('display', 'none');
  });

  // Allow mouse over of details without hiding details
  $('#previewPopupContainer').mouseover(function()
  {
      if (hideTimer)
          clearTimeout(hideTimer);
  });

  // Hide after mouseout
  $('#previewPopupContainer').mouseout(function()
  {
      if (hideTimer)
          clearTimeout(hideTimer);
      hideTimer = setTimeout(function()
      {
          container.css('display', 'none');
      }, hideDelay);
  });
};

function positionToolTip(e) {
        var offsetFromTop = e.pageY - viewport.scrollTop();
        var offsetFromLeft = e.pageX - viewport.scrollLeft();
        var tooltipObj = $('#previewPopupContainer');
        var pxToBottom = viewport.height() - (e.pageY - viewport.scrollTop());
        var pxToRight = viewport.width() - (e.pageX - viewport.scrollLeft());
        var cssTop = 0;
        var cssLeft = 0;
        var topMargin = parseFloat(tooltipObj.css('marginTop'));
        if (isNaN(topMargin)) {
            topMargin = 0;
        }
        var leftMargin = parseFloat(tooltipObj.css('marginLeft'));
        if (isNaN(leftMargin)) {
            leftMargin = 0;
        }
        var topPadding = parseFloat(tooltipObj.css('paddingTop'));
        if (isNaN(topPadding)) {
            topPadding = 0;
        }
        var leftPadding = parseFloat(tooltipObj.css('paddingLeft'));
        if (isNaN(leftPadding)) {
            leftPadding = 0;
        }
        var topBorder = parseFloat(tooltipObj.css('border-top-width'));
        if (isNaN(topBorder)) {
            topBorder = 0;
        }
        var leftBorder = parseFloat(tooltipObj.css('border-left-width'));
        if (isNaN(leftBorder)) {
            leftBorder = 0;
        }
        var topOffset = topMargin + topPadding + topBorder;
        var leftOffset = leftMargin + leftPadding + leftBorder;

        if (tooltipObj.height() > viewport.height()) {
            cssTop = viewport.scrollTop() - topOffset + topPadding;
        }
        else if (tooltipObj.height() > pxToBottom) {
            cssTop = viewport.scrollTop() + (viewport.height() - tooltipObj.height()) - topOffset - topPadding - topBorder;
        }
        else {
            cssTop = e.pageY - xOffset;
        }

        if (tooltipObj.width() > viewport.width()) {
            cssLeft = viewport.scrollLeft() - leftOffset + leftPadding;
        }
        else if (tooltipObj.width() > pxToRight) {
            cssLeft = viewport.scrollLeft() + (viewport.width() - tooltipObj.width()) - leftOffset - leftPadding - leftBorder;
        }
        else {
            cssLeft = e.pageX + yOffset;
        }

        tooltipObj.css({ top: cssTop, left: cssLeft }).fadeIn(fadeInTime);
        $('tooltipPopupPopup').show();
    }
