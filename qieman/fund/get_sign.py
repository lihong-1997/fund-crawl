import execjs
import requests


def get_sign():
    sign = execjs.compile("""
    rb = function(e) {
                    return function(e) {
                        return e.map((function(e) {
                            return t = e.toString(16),
                            n = 2,
                            t.length > n ? t : Array(n - t.length + 1).join("0") + t;
                            var t, n
                        }
                        )).join("")
                    }(e)
                }
rcb = function(e) {
                    return e.map((function(e) {
                        return String.fromCharCode(e)
                    }
                    )).join("")
                }
nstb = function(e) {
                    return e.split("").map((function(e) {
                        return e.charCodeAt(0)
                    }
                    ))
                }
rcus = function(e) {
                    return nstb(unescape(encodeURIComponent(e)))
                }
var i = [];
            !function() {
                function e(e) {
                    for (var t = Math.sqrt(e), n = 2; n <= t; n++)
                        if (!(e % n))
                            return !1;
                    return !0
                }
                function t(e) {
                    return 4294967296 * (e - (0 | e)) | 0
                }
                for (var n = 2, r = 0; r < 64; )
                    e(n) && (i[r] = t(Math.pow(n, 1 / 3)),
                    r++),
                    n++
            }();
var o = []
a = function(e, t, n) {
                for (var r = e[0], a = e[1], s = e[2], u = e[3], c = e[4], l = e[5], f = e[6], p = e[7], d = 0; d < 64; d++) {
                    if (d < 16)
                        o[d] = 0 | t[n + d];
                    else {
                        var h = o[d - 15]
                          , v = (h << 25 | h >>> 7) ^ (h << 14 | h >>> 18) ^ h >>> 3
                          , y = o[d - 2]
                          , m = (y << 15 | y >>> 17) ^ (y << 13 | y >>> 19) ^ y >>> 10;
                        o[d] = v + o[d - 7] + m + o[d - 16]
                    }
                    var g = r & a ^ r & s ^ a & s
                      , b = (r << 30 | r >>> 2) ^ (r << 19 | r >>> 13) ^ (r << 10 | r >>> 22)
                      , _ = p + ((c << 26 | c >>> 6) ^ (c << 21 | c >>> 11) ^ (c << 7 | c >>> 25)) + (c & l ^ ~c & f) + i[d] + o[d];
                    p = f,
                    f = l,
                    l = c,
                    c = u + _ | 0,
                    u = s,
                    s = a,
                    a = r,
                    r = _ + (b + g) | 0
                }
                e[0] = e[0] + r | 0,
                e[1] = e[1] + a | 0,
                e[2] = e[2] + s | 0,
                e[3] = e[3] + u | 0,
                e[4] = e[4] + c | 0,
                e[5] = e[5] + l | 0,
                e[6] = e[6] + f | 0,
                e[7] = e[7] + p | 0
            };
function s(e, t) {
                e.constructor === String && (e = rcus(e));
                var n = [1779033703, 3144134277, 1013904242, 2773480762, 1359893119, 2600822924, 528734635, 1541459225]
                  , i = function(e) {
                    for (var t = [], n = 0, r = 0; n < e.length; n++,
                    r += 8)
                        t[r >>> 5] |= e[n] << 24 - r % 32;
                    return t
                }(e)
                  , o = 8 * e.length;
                i[o >> 5] |= 128 << 24 - o % 32,
                i[15 + (o + 64 >> 9 << 4)] = o;
                for (var s = 0; s < i.length; s += 16)
                    a(n, i, s);
                var u = function(e) {
                    for (var t = [], n = 0; n < 32 * e.length; n += 8)
                        t.push(e[n >>> 5] >>> 24 - n % 32 & 255);
                    return t
                }(n);
                return t && t.asBytes ? u : t && t.asString ? rcb(u) : rb(u)
            }
function get_xsign() {
            var e = Date.now();
            return e + s(Math.floor(1.01 * e).toString()).toUpperCase().substring(0, 32)
        }

""")
    x_sign = sign.call('get_xsign')
    return x_sign

if __name__ == "__main__":
    x_sign = get_sign()
    print(x_sign)
