(function ($) {
	var h = new Array();
	var j = new Array();
	var k = 0;
	$.fn.popupmenu = function (c) {
		var d = {
			target: false,
			addStyle: false,
			time: 300,
			speed: "",
			autooff: true
		};
		var c = $.extend(d, c);
console.log(c);
		var e = false;
		var f = false;
		var g;
		return this.each(function () {
			var a = $(this);
			var b = $(c.target);
			h[k] = b;
			j[k] = a;
			k++;
			a.mouseover(function () {
//				$.fx.off = true;
				if (c.autooff) {
					$.each(h, function (i, n) {
						n.slideUp(0)
					});
					$.each(j, function (i, n) {
						n.removeClass(c.addStyle)
					})
				}
				clearTimeout(g);
				if (c.addStyle != false) {
					a.addClass(c.addStyle)
				}
				b.slideDown(100)
//				$.fx.off = false;
			});
			a.mouseout(function () {
				if (!e) {
					g = setTimeout(function () {
						if (c.addStyle != false) {
							a.removeClass(c.addStyle)
						}
						b.slideUp(0)
					},
					c.time)
				}
			});
			b.mouseover(function () {
				e = true;
				clearTimeout(g)
			});
			b.mouseout(function () {
				e = false;
				g = setTimeout(function () {
					if (c.addStyle != false) {
						a.removeClass(c.addStyle)
					}
					b.slideUp(0)
				},
				c.time)
			})
		})
	}
})(jQuery);
