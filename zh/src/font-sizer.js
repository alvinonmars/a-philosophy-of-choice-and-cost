// Reading controls for 人选天选论
// Font size, line height, and font family — saves to localStorage

(function() {
    'use strict';

    var KEYS = {
        size: 'book-font-size',
        height: 'book-line-height',
        font: 'book-font-family'
    };

    var FONTS = [
        { name: 'Default', value: 'system-ui, -apple-system, "PingFang SC", "Microsoft YaHei", sans-serif' },
        { name: 'Serif', value: '"Noto Serif SC", "Source Han Serif SC", "Songti SC", serif' },
        { name: 'Sans', value: '"Noto Sans SC", "Source Han Sans SC", "PingFang SC", "Hiragino Sans GB", sans-serif' }
    ];

    var SIZE = { min: 14, max: 26, step: 2, def: 18 };
    var LH = { min: 1.4, max: 2.6, step: 0.2, def: 1.8 };

    var state = {
        size: parseInt(localStorage.getItem(KEYS.size)) || SIZE.def,
        height: parseFloat(localStorage.getItem(KEYS.height)) || LH.def,
        fontIdx: parseInt(localStorage.getItem(KEYS.font)) || 0
    };

    function clamp(v, min, max) { return Math.max(min, Math.min(max, v)); }

    function apply() {
        state.size = clamp(state.size, SIZE.min, SIZE.max);
        state.height = parseFloat(clamp(state.height, LH.min, LH.max).toFixed(1));
        state.fontIdx = state.fontIdx % FONTS.length;

        localStorage.setItem(KEYS.size, state.size);
        localStorage.setItem(KEYS.height, state.height);
        localStorage.setItem(KEYS.font, state.fontIdx);

        var main = document.querySelector('.content main');
        if (!main) return;

        var css = 'font-size:' + state.size + 'px !important;'
            + 'line-height:' + state.height + ' !important;'
            + 'font-family:' + FONTS[state.fontIdx].value + ' !important;';

        main.style.cssText = css;

        // Apply to child elements to override CSS specificity
        var els = main.querySelectorAll('p, li, blockquote, blockquote p');
        for (var i = 0; i < els.length; i++) {
            els[i].style.fontSize = state.size + 'px';
            els[i].style.lineHeight = state.height;
            els[i].style.fontFamily = FONTS[state.fontIdx].value;
        }

        updateLabels();
    }

    function updateLabels() {
        var el;
        el = document.getElementById('rc-size'); if (el) el.textContent = state.size;
        el = document.getElementById('rc-lh'); if (el) el.textContent = state.height.toFixed(1);
        el = document.getElementById('rc-font'); if (el) el.textContent = FONTS[state.fontIdx].name;
    }

    function btn(text, title, onclick) {
        var b = document.createElement('button');
        b.textContent = text;
        b.title = title;
        b.style.cssText = 'border:1px solid #ccc;background:#faf8f4;border-radius:4px;'
            + 'min-width:28px;height:28px;cursor:pointer;font-size:13px;'
            + 'display:flex;align-items:center;justify-content:center;'
            + 'color:#444;touch-action:manipulation;-webkit-tap-highlight-color:transparent;'
            + 'padding:0 4px;';
        b.onclick = onclick;
        return b;
    }

    function label(id, width) {
        var s = document.createElement('span');
        s.id = id;
        s.style.cssText = 'min-width:' + (width || 24) + 'px;text-align:center;font-size:11px;color:#666;';
        return s;
    }

    function row(items) {
        var d = document.createElement('div');
        d.style.cssText = 'display:flex;align-items:center;gap:4px;';
        for (var i = 0; i < items.length; i++) d.appendChild(items[i]);
        return d;
    }

    function createControls() {
        var bar = document.createElement('div');
        bar.id = 'reading-controls';
        bar.style.cssText = 'position:fixed;bottom:16px;right:16px;z-index:1000;'
            + 'background:rgba(255,255,255,0.96);border:1px solid #ddd;'
            + 'border-radius:10px;padding:8px 10px;'
            + 'box-shadow:0 2px 12px rgba(0,0,0,0.12);'
            + 'font-family:system-ui,sans-serif;font-size:12px;color:#555;'
            + 'display:flex;flex-direction:column;gap:6px;'
            + 'transition:opacity 0.2s;';

        // Toggle button (collapse/expand)
        var toggle = document.createElement('button');
        toggle.textContent = 'Aa';
        toggle.style.cssText = 'position:absolute;top:-14px;right:8px;'
            + 'border:1px solid #ccc;background:#fff;border-radius:12px;'
            + 'width:28px;height:28px;cursor:pointer;font-size:12px;font-weight:600;'
            + 'color:#555;box-shadow:0 1px 4px rgba(0,0,0,0.1);'
            + 'display:flex;align-items:center;justify-content:center;';

        var panel = document.createElement('div');
        panel.style.cssText = 'display:flex;flex-direction:column;gap:6px;';

        var collapsed = false;
        toggle.onclick = function() {
            collapsed = !collapsed;
            panel.style.display = collapsed ? 'none' : 'flex';
            bar.style.padding = collapsed ? '16px 10px 4px' : '8px 10px';
        };

        // Font size row
        panel.appendChild(row([
            btn('\u2212', 'Smaller', function() { state.size -= SIZE.step; apply(); }),
            label('rc-size', 20),
            btn('+', 'Larger', function() { state.size += SIZE.step; apply(); }),
            document.createTextNode(' '),
        ]));

        // Line height row
        var lhLabel = document.createElement('span');
        lhLabel.textContent = '\u2195';
        lhLabel.style.cssText = 'font-size:14px;margin-right:2px;';
        panel.appendChild(row([
            btn('\u2212', 'Tighter', function() { state.height -= LH.step; apply(); }),
            label('rc-lh', 24),
            btn('+', 'Looser', function() { state.height += LH.step; apply(); }),
        ]));

        // Font family row
        panel.appendChild(row([
            btn('\u25C0', 'Prev font', function() { state.fontIdx = (state.fontIdx + FONTS.length - 1) % FONTS.length; apply(); }),
            label('rc-font', 44),
            btn('\u25B6', 'Next font', function() { state.fontIdx = (state.fontIdx + 1) % FONTS.length; apply(); }),
        ]));

        // Reset
        panel.appendChild(row([
            btn('\u21BA Reset', 'Reset all', function() {
                state.size = SIZE.def; state.height = LH.def; state.fontIdx = 0; apply();
            }),
        ]));

        bar.appendChild(toggle);
        bar.appendChild(panel);
        document.body.appendChild(bar);
    }

    function init() {
        createControls();
        apply();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
