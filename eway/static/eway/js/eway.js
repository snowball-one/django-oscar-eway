(function () {
    var a = this;
    this.eWAY = function () {
        function a() {}
        return a.version = 1, a.path = "JSONP/v3/process", a.processing = false, a.defaults = {
            autoRedirect: true,
            onComplete: null,
            on3DSecure: null,
            onRedirecting: function (a) {
                return true
            },
            onError: null,
            onTimeout: null,
            timeout: 9e4
        }, a.isValidCvn = function (b) {
            return b = a.trim(b), /^\d+$/.test(b) && b.length >= 3 && b.length <= 4
        }, a.isValidCardNumber = function (b) {
            return b = (b + "").replace(/\s+|-/g, ""), b.length >= 10 && b.length <= 19 && a.isValidLuhn(b)
        }, a.process = function (b, c) {
            var d, e = "&",
                f = (new Date).getTime(),
                g = 0,
                h, i;
            if (a.processing) return;
            a.processing = true;
            var j = a.parseUri(b.getAttribute('action'));
            console.log(b, b.getAttribute('action'));
            var k = "eWAY" + (++f).toString(36);
            c = a.merge(a.defaults, c);
            window[k] = function (a) {
                if (a.Is3DSecure && c.on3DSecure != null) c.on3DSecure();
                if (c.autoRedirect && c.onRedirecting != null && c.onRedirecting(a.RedirectUrl)) window.location = a.RedirectUrl;
                if (c.onComplete != null) c.onComplete(a);
                try {
                    delete window[k]
                } catch (b) {}
                window[k] = void 0
            };
            for (var l = 0; l < b.elements.length; l++) {
                d = b.elements[l];
                if (/EWAY_.*/.test(d.name)) e += a.encode(d.name) + "=" + a.encode(a.trim(d.value)) + "&"
            }
            h = document.head || document.getElementsByTagName("head")[0] || document.documentElement;
            i = j.protocol + "://" + j.authority + "/" + a.path + "?ewayjsonp=" + k + e;
            var m = document.createElement("script");
            m.setAttribute("type", "text/javascript");
            m.setAttribute("src", i);
            m.async = true;
            m.onload = function () {
                n()
            };
            m.onerror = function (a) {
                if (c.onError != null) c.onError(a);
                n()
            };
            h.appendChild(m);
            g = setTimeout(function () {
                if (c.onTimeout != null) c.onTimeout();
                n()
            }, c.timeout);
            var n = function () {
                try {
                    a.processing = false;
                    h.removeChild(m)
                } catch (b) {}
                clearTimeout(g);
                if (k in window) window[k] = function () {}
            }
        }, a
    }(),
    function () {
        this.eWAY.merge = function (a, b) {
            var c = {};
            for (var d in a) {
                c[d] = a[d]
            }
            for (var d in b) {
                c[d] = b[d]
            }
            return c
        }, this.eWAY.encode = function (a) {
            return encodeURIComponent(a)
        }, this.eWAY.trim = function (a) {
            return (a + "").replace(/^\s+|\s+$/g, "")
        }, this.eWAY.parseUri = function (a) {
            var b = ["source", "protocol", "authority", "domain", "port", "path", "directoryPath", "fileName", "query", "anchor"],
                c = (new RegExp("^(?:([^:/?#.]+):)?(?://)?(([^:/?#]*)(?::(\\d*))?)((/(?:[^?#](?![^?#/]*\\.[^?#/.]+(?:[\\?#]|$)))*/?)?([^?#/]*))?(?:\\?([^#]*))?(?:#(.*))?")).exec(a),
                d = {};
            for (var e = 0; e < 10; e++) d[b[e]] = c[e] ? c[e] : "";
            if (d.directoryPath.length > 0) d.directoryPath = d.directoryPath.replace(/\/?$/, "/");
            return d
        }, this.eWAY.isValidLuhn = function (a) {
            var b, c, d, e, a, f;
            d = !0, e = 0, c = (a + "").split("").reverse();
            for (a = 0, f = c.length; a < f; a++) {
                b = c[a], b = parseInt(b, 10);
                if (d = !d) b *= 2;
                b > 9 && (b -= 9), e += b
            }
            return e % 10 === 0
        }
    }()
})()
