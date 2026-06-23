// ============================================================
// 🚀 MARDUK-TRADING-RIG™ - DASHBOARD APP
// ============================================================
//
// Real-time dashboard updates via WebSocket/API polling
//
// © 2026 Seliim Ahmed. All Rights Reserved.
//
// ============================================================

(function() {
    'use strict';

    // ============================================================
    // 🔧 CONFIGURATION
    // ============================================================

    const CONFIG = {
        API_URL: 'http://localhost:8080/api',
        WS_URL: 'ws://localhost:8080/ws',
        UPDATE_INTERVAL: 5000, // 5 seconds
        RETRY_INTERVAL: 10000, // 10 seconds
        MAX_LOG_LINES: 50,
        RECONNECT_DELAY: 3000
    };

    // ============================================================
    // 🧠 STATE
    // ============================================================

    const state = {
        connected: false,
        data: {
            account: { balance: 0, equity: 0, pnl: 0, marginLevel: 0 },
            signal: { action: 'HOLD', confidence: 0, entry: 0, sl: 0, tp: 0, rr: 0 },
            energy: { node3: false, node6: false, node9: false, confluence: 'C0' },
            fibonacci: { f236: 0, f382: 0, f500: 0, f618: 0, f786: 0 },
            positions: [],
            terminal: []
        },
        terminalLines: []
    };

    // ============================================================
    // 📡 DOM REFS
    // ============================================================

    const DOM = {};

    function cacheDOMElements() {
        DOM.headerTime = document.getElementById('headerTime');
        DOM.balance = document.getElementById('balance');
        DOM.equity = document.getElementById('equity');
        DOM.pnl = document.getElementById('pnl');
        DOM.marginLevel = document.getElementById('marginLevel');
        DOM.signalAction = document.getElementById('signalAction');
        DOM.signalConfidence = document.getElementById('signalConfidence');
        DOM.signalEntry = document.getElementById('signalEntry');
        DOM.signalSL = document.getElementById('signalSL');
        DOM.signalTP = document.getElementById('signalTP');
        DOM.signalRR = document.getElementById('signalRR');
        DOM.node3 = document.getElementById('node3');
        DOM.node6 = document.getElementById('node6');
        DOM.node9 = document.getElementById('node9');
        DOM.confluenceLevel = document.getElementById('confluenceLevel');
        DOM.fib236 = document.getElementById('fib236');
        DOM.fib382 = document.getElementById('fib382');
        DOM.fib500 = document.getElementById('fib500');
        DOM.fib618 = document.getElementById('fib618');
        DOM.fib786 = document.getElementById('fib786');
        DOM.positionsContainer = document.getElementById('positionsContainer');
        DOM.terminal = document.getElementById('terminal');
    }

    // ============================================================
    // 🕐 CLOCK
    // ============================================================

    function updateClock() {
        const now = new Date();
        const timeStr = now.toLocaleTimeString('en-US', { hour12: false });
        if (DOM.headerTime) {
            DOM.headerTime.textContent = timeStr;
        }
    }

    // ============================================================
    // 📝 TERMINAL
    // ============================================================

    function addTerminalLine(message, type = 'info') {
        const timestamp = new Date().toLocaleTimeString('en-US', { hour12: false });
        const line = {
            timestamp,
            message,
            type
        };

        state.terminalLines.push(line);
        if (state.terminalLines.length > CONFIG.MAX_LOG_LINES) {
            state.terminalLines.shift();
        }

        renderTerminal();
    }

    function renderTerminal() {
        if (!DOM.terminal) return;

        let html = '';
        for (const line of state.terminalLines) {
            const typeClass = line.type || 'info';
            html += `<div class="terminal-line ${typeClass}">
                <span class="timestamp">${line.timestamp}</span>
                ${line.message}
            </div>`;
        }

        DOM.terminal.innerHTML = html;
        DOM.terminal.scrollTop = DOM.terminal.scrollHeight;
    }

    // ============================================================
    // 📊 RENDER FUNCTIONS
    // ============================================================

    function renderAccount(data) {
        if (data.balance !== undefined) {
            DOM.balance.textContent = `$${data.balance.toFixed(2)}`;
        }
        if (data.equity !== undefined) {
            DOM.equity.textContent = `$${data.equity.toFixed(2)}`;
        }
        if (data.pnl !== undefined) {
            const pnl = data.pnl;
            DOM.pnl.textContent = `$${pnl.toFixed(2)}`;
            DOM.pnl.className = 'metric-value ' + (pnl > 0 ? 'positive' : pnl < 0 ? 'negative' : 'neutral');
        }
        if (data.marginLevel !== undefined) {
            DOM.marginLevel.textContent = `${data.marginLevel.toFixed(2)}%`;
        }
    }

    function renderSignal(data) {
        const action = data.action || 'HOLD';
        DOM.signalAction.textContent = action;
        DOM.signalAction.className = 'signal-action ' + action.toLowerCase();

        DOM.signalConfidence.textContent = `${data.confidence || 0}%`;
        DOM.signalEntry.textContent = data.entry ? data.entry.toFixed(5) : '--';
        DOM.signalSL.textContent = data.sl ? data.sl.toFixed(5) : '--';
        DOM.signalTP.textContent = data.tp ? data.tp.toFixed(5) : '--';
        DOM.signalRR.textContent = data.rr ? data.rr.toFixed(2) : '--';
    }

    function renderEnergy(data) {
        const nodes = [
            { id: DOM.node3, active: data.node3, label: '3:00' },
            { id: DOM.node6, active: data.node6, label: '6:00' },
            { id: DOM.node9, active: data.node9, label: '9:00' }
        ];

        for (const node of nodes) {
            if (!node.id) continue;
            const statusEl = node.id.querySelector('.node-status');
            if (node.active) {
                node.id.classList.add('active');
                statusEl.textContent = '🟢';
                statusEl.className = 'node-status active';
            } else {
                node.id.classList.remove('active');
                statusEl.textContent = '⚪';
                statusEl.className = 'node-status inactive';
            }
        }

        DOM.confluenceLevel.textContent = data.confluence || 'C0';
    }

    function renderFibonacci(data) {
        const fibs = [
            { id: DOM.fib236, value: data.f236 },
            { id: DOM.fib382, value: data.f382 },
            { id: DOM.fib500, value: data.f500 },
            { id: DOM.fib618, value: data.f618 },
            { id: DOM.fib786, value: data.f786 }
        ];

        for (const fib of fibs) {
            if (!fib.id) continue;
            const val = fib.value || 0;
            fib.id.textContent = `${val.toFixed(1)}%`;
            fib.id.className = 'fib-prob ' + (val > 60 ? 'high' : val > 40 ? 'medium' : 'low');
        }
    }

    function renderPositions(positions) {
        if (!DOM.positionsContainer) return;

        if (!positions || positions.length === 0) {
            DOM.positionsContainer.innerHTML = '<div class="position-empty">No open positions</div>';
            return;
        }

        let html = `
            <div class="position-row header">
                <span>Symbol</span>
                <span>Action</span>
                <span>Volume</span>
                <span>Entry</span>
                <span>Current</span>
                <span>P&L</span>
            </div>
        `;

        for (const pos of positions) {
            const pnl = pos.pnl || 0;
            html += `
                <div class="position-row">
                    <span class="pos-symbol">${pos.symbol || '--'}</span>
                    <span class="pos-action ${(pos.action || '').toLowerCase()}">${pos.action || '--'}</span>
                    <span>${pos.volume || '--'}</span>
                    <span>${pos.entry ? pos.entry.toFixed(5) : '--'}</span>
                    <span>${pos.current ? pos.current.toFixed(5) : '--'}</span>
                    <span class="pos-pnl ${pnl > 0 ? 'positive' : pnl < 0 ? 'negative' : ''}">
                        ${pnl > 0 ? '+' : ''}${pnl.toFixed(2)}
                    </span>
                </div>
            `;
        }

        DOM.positionsContainer.innerHTML = html;
    }

    // ============================================================
    // 🔄 UPDATE FUNCTIONS
    // ============================================================

    function updateDashboard(data) {
        if (!data) return;

        if (data.account) renderAccount(data.account);
        if (data.signal) renderSignal(data.signal);
        if (data.energy) renderEnergy(data.energy);
        if (data.fibonacci) renderFibonacci(data.fibonacci);
        if (data.positions) renderPositions(data.positions);
    }

    // ============================================================
    // 🌐 API CALLS
    // ============================================================

    async function fetchData() {
        try {
            const response = await fetch(`${CONFIG.API_URL}/dashboard`);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            const data = await response.json();
            state.data = data;
            updateDashboard(data);
            state.connected = true;
        } catch (error) {
            console.warn('API fetch failed:', error);
            state.connected = false;
            // Don't clear dashboard on error - keep last known data
        }
    }

    // ============================================================
    // 🔌 WEBSOCKET (optional - for future use)
    // ============================================================

    let ws = null;
    let wsReconnectTimer = null;

    function connectWebSocket() {
        try {
            ws = new WebSocket(CONFIG.WS_URL);

            ws.onopen = function() {
                console.log('✅ WebSocket connected');
                addTerminalLine('WebSocket connected', 'success');
                state.connected = true;
            };

            ws.onmessage = function(event) {
                try {
                    const data = JSON.parse(event.data);
                    if (data.type === 'update') {
                        state.data = data.payload;
                        updateDashboard(data.payload);
                    } else if (data.type === 'terminal') {
                        addTerminalLine(data.message, data.level || 'info');
                    }
                } catch (e) {
                    console.warn('WS parse error:', e);
                }
            };

            ws.onclose = function() {
                console.log('WebSocket disconnected');
                addTerminalLine('WebSocket disconnected', 'warning');
                state.connected = false;
                scheduleReconnect();
            };

            ws.onerror = function(error) {
                console.warn('WebSocket error:', error);
                // onclose will be called after error
            };

        } catch (error) {
            console.warn('WebSocket connection failed:', error);
            scheduleReconnect();
        }
    }

    function scheduleReconnect() {
        if (wsReconnectTimer) clearTimeout(wsReconnectTimer);
        wsReconnectTimer = setTimeout(() => {
            addTerminalLine('Attempting to reconnect WebSocket...', 'warning');
            connectWebSocket();
        }, CONFIG.RECONNECT_DELAY);
    }

    // ============================================================
    // 🚀 INITIALIZATION
    // ============================================================

    function init() {
        // Cache DOM elements
        cacheDOMElements();

        // Add welcome message
        addTerminalLine('🚀 MARDUK-TRADING-RIG™ v1.0', 'success');
        addTerminalLine('📡 Dashboard initializing...', 'info');

        // Start clock
        updateClock();
        setInterval(updateClock, 1000);

        // Initial data fetch
        fetchData();

        // Periodic updates
        setInterval(fetchData, CONFIG.UPDATE_INTERVAL);

        // Try WebSocket connection
        try {
            connectWebSocket();
        } catch (e) {
            addTerminalLine('WebSocket not available. Using polling mode.', 'warning');
        }

        addTerminalLine('✅ Dashboard ready', 'success');

        // Log connection status every 30 seconds
        setInterval(() => {
            const status = state.connected ? 'connected' : 'disconnected';
            // Only log if we have something to say
            if (!state.connected) {
                addTerminalLine(`⚠️ Waiting for connection...`, 'warning');
            }
        }, 30000);
    }

    // ============================================================
    // 🏁 START
    // ============================================================

    // Run when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();
