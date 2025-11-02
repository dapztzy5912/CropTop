// Variabel global
let isSpamming = false;
let sentCount = 0;
let failedCount = 0;
let totalCount = 0;
let currentAttackId = null;

// Elemen DOM
const startBtn = document.getElementById('startBtn');
const resetBtn = document.getElementById('resetBtn');
const sentCountEl = document.getElementById('sentCount');
const failedCountEl = document.getElementById('failedCount');
const successRateEl = document.getElementById('successRate');
const progressEl = document.getElementById('progress');
const progressBar = document.getElementById('progressBar');
const logContainer = document.getElementById('logContainer');
const apiStatusEl = document.getElementById('apiStatus');

// Base URL untuk API (akan menyesuaikan dengan domain Vercel)
const API_BASE = window.location.origin + '/api';

// Fungsi untuk menambahkan log
function addLog(message, type = 'info') {
    const logEntry = document.createElement('div');
    logEntry.className = `log-entry log-${type}`;
    logEntry.textContent = `[${new Date().toLocaleTimeString()}] ${message}`;
    logContainer.appendChild(logEntry);
    logContainer.scrollTop = logContainer.scrollHeight;
}

// Fungsi untuk memperbarui statistik
function updateStats() {
    sentCountEl.textContent = sentCount;
    failedCountEl.textContent = failedCount;
    
    const totalSent = sentCount + failedCount;
    const successRate = totalSent > 0 ? Math.round((sentCount / totalSent) * 100) : 0;
    successRateEl.textContent = `${successRate}%`;
    
    const progress = totalCount > 0 ? Math.round((totalSent / totalCount) * 100) : 0;
    progressEl.textContent = `${progress}%`;
    progressBar.style.width = `${progress}%`;
}

// Fungsi untuk mengecek status API
async function checkAPIStatus() {
    try {
        const response = await fetch(`${API_BASE}/status`);
        if (response.ok) {
            apiStatusEl.textContent = 'API Online';
            apiStatusEl.className = 'status-online';
            return true;
        } else {
            throw new Error('API not responding');
        }
    } catch (error) {
        apiStatusEl.textContent = 'API Offline';
        apiStatusEl.className = 'status-offline';
        addLog('❌ Backend API offline', 'error');
        return false;
    }
}

// Fungsi untuk memulai spam
async function startSpam() {
    const username = document.getElementById('username').value.trim();
    const message = document.getElementById('message').value.trim();
    const count = parseInt(document.getElementById('count').value);
    const delay = parseFloat(document.getElementById('delay').value);

    if (!username || !message) {
        addLog('❌ Username dan pesan harus diisi!', 'error');
        return;
    }

    if (count < 1 || count > 50) {
        addLog('❌ Jumlah pesan harus antara 1-50!', 'error');
        return;
    }

    // Cek status API terlebih dahulu
    const apiOnline = await checkAPIStatus();
    if (!apiOnline) {
        addLog('❌ Tidak dapat terhubung ke backend API', 'error');
        return;
    }

    isSpamming = true;
    totalCount = count;
    sentCount = 0;
    failedCount = 0;

    // Update UI
    startBtn.disabled = true;
    startBtn.querySelector('.btn-text').style.display = 'none';
    startBtn.querySelector('.btn-loader').style.display = 'flex';

    addLog(`🚀 Mengirim spam ke ${username} dengan ${count} pesan...`, 'info');

    try {
        const response = await fetch(`${API_BASE}/start`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                username: username,
                message: message,
                count: count,
                delay: delay
            })
        });

        const data = await response.json();

        if (response.ok) {
            currentAttackId = data.attack_id;
            sentCount = data.stats.sent;
            failedCount = data.stats.failed;
            
            addLog(`✅ Spam selesai! ${sentCount} berhasil, ${failedCount} gagal`, 'success');
            addLog(`📊 Success rate: ${data.stats.success_rate}%`, 'info');
            
            // Tampilkan hasil detail
            data.results.forEach(result => {
                if (result.success) {
                    addLog(`✅ Pesan ${result.attempt} berhasil dikirim`, 'success');
                } else {
                    addLog(`❌ Pesan ${result.attempt} gagal dikirim`, 'error');
                }
            });
        } else {
            addLog(`❌ Error: ${data.error}`, 'error');
        }
    } catch (error) {
        addLog(`❌ Network error: ${error.message}`, 'error');
    } finally {
        // Reset UI
        startBtn.disabled = false;
        startBtn.querySelector('.btn-text').style.display = 'block';
        startBtn.querySelector('.btn-loader').style.display = 'none';
        isSpamming = false;
        updateStats();
    }
}

// Fungsi untuk mereset statistik
function resetStats() {
    if (isSpamming) {
        addLog('⚠️ Harap tunggu spam selesai sebelum reset', 'warning');
        return;
    }
    
    sentCount = 0;
    failedCount = 0;
    totalCount = 0;
    currentAttackId = null;
    updateStats();
    logContainer.innerHTML = '<div class="log-entry log-info">Siap memulai spam...</div>';
    addLog('📊 Statistik telah direset', 'info');
}

// Event listeners
startBtn.addEventListener('click', startSpam);
resetBtn.addEventListener('click', resetStats);

// Inisialisasi
updateStats();
checkAPIStatus();

// Cek status API setiap 30 detik
setInterval(checkAPIStatus, 30000);
