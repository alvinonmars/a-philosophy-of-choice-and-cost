// Font size adjuster for 人选天选论
// Adds A-/A+ controls, saves preference to localStorage

(function() {
    'use strict';

    var STORAGE_KEY = 'book-font-size';
    var MIN = 14;
    var MAX = 26;
    var STEP = 2;
    var DEFAULT = 18;

    var currentSize = parseInt(localStorage.getItem(STORAGE_KEY)) || DEFAULT;

    function applySize(px) {
        currentSize = Math.max(MIN, Math.min(MAX, px));
        localStorage.setItem(STORAGE_KEY, currentSize);
        var main = document.querySelector('.content main');
        if (main) {
            main.style.fontSize = currentSize + 'px';
            // Also apply to p and li to override any specificity issues
            var els = main.querySelectorAll('p, li, blockquote');
            for (var i = 0; i < els.length; i++) {
                els[i].style.fontSize = currentSize + 'px';
            }
        }
        updateLabel();
    }

    function updateLabel() {
        var label = document.getElementById('font-size-label');
        if (label) {
            label.textContent = currentSize + 'px';
        }
    }

    function createControls() {
        var bar = document.createElement('div');
        bar.id = 'font-sizer';
        bar.style.cssText = 'position:fixed;bottom:20px;right:20px;z-index:1000;'
            + 'display:flex;align-items:center;gap:6px;'
            + 'background:rgba(255,255,255,0.95);border:1px solid #ddd;'
            + 'border-radius:8px;padding:6px 10px;'
            + 'box-shadow:0 2px 8px rgba(0,0,0,0.1);'
            + 'font-family:system-ui,sans-serif;font-size:14px;color:#555;';

        var btnMinus = document.createElement('button');
        btnMinus.textContent = 'A\u2212';
        btnMinus.title = 'Decrease font size';
        btnMinus.style.cssText = btnStyle();
        btnMinus.onclick = function() { applySize(currentSize - STEP); };

        var label = document.createElement('span');
        label.id = 'font-size-label';
        label.style.cssText = 'min-width:40px;text-align:center;font-size:12px;';

        var btnPlus = document.createElement('button');
        btnPlus.textContent = 'A+';
        btnPlus.title = 'Increase font size';
        btnPlus.style.cssText = btnStyle();
        btnPlus.onclick = function() { applySize(currentSize + STEP); };

        var btnReset = document.createElement('button');
        btnReset.textContent = '\u21BA';
        btnReset.title = 'Reset to default';
        btnReset.style.cssText = btnStyle() + 'font-size:16px;';
        btnReset.onclick = function() { applySize(DEFAULT); };

        bar.appendChild(btnMinus);
        bar.appendChild(label);
        bar.appendChild(btnPlus);
        bar.appendChild(btnReset);
        document.body.appendChild(bar);
    }

    function btnStyle() {
        return 'border:1px solid #ccc;background:#faf8f4;border-radius:4px;'
            + 'width:32px;height:32px;cursor:pointer;font-size:14px;'
            + 'display:flex;align-items:center;justify-content:center;'
            + 'color:#444;touch-action:manipulation;-webkit-tap-highlight-color:transparent;';
    }

    // Init on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    function init() {
        createControls();
        applySize(currentSize);
    }
})();
