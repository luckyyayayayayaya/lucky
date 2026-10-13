(function () {
  const tooth = new ToothAnimator();
  const garden = new GardenRenderer();

  const input = document.getElementById('thoughtInput');
  const submitBtn = document.getElementById('submitBtn');
  const charCount = document.getElementById('charCount');
  const drawToggle = document.getElementById('historyToggle');
  const drawer = document.getElementById('historyDrawer');
  const drawerClose = document.getElementById('drawerClose');
  const drawerList = document.getElementById('drawerList');
  const toast = document.getElementById('toast');

  let overlay = null;

  // ---- Init ----
  function init() {
    updateDate();
    checkDailyMessage();
    garden.refresh();
    updateStats();
    bindEvents();
    checkNightMode();
    setInterval(checkNightMode, 15 * 60 * 1000);
  }

  function updateDate() {
    const now = new Date();
    const days = ['日', '一', '二', '三', '四', '五', '六'];
    const str = `${now.getFullYear()}年${now.getMonth()+1}月${now.getDate()}日 星期${days[now.getDay()]}`;
    document.getElementById('dateText').textContent = str;
  }

  function checkNightMode() {
    const hour = new Date().getHours();
    if (hour >= 23 || hour < 5) {
      tooth.setState('sleeping');
      tooth.showBubble('zzz... 好运牙在睡觉，明天见~', false);
    }
  }

  // ---- Daily message ----
  async function checkDailyMessage() {
    const hour = new Date().getHours();
    const morningCard = document.getElementById('morningCard');
    const eveningCard = document.getElementById('eveningCard');
    const placeholder = document.getElementById('dailyPlaceholder');

    morningCard.classList.remove('visible');
    eveningCard.classList.remove('visible');
    placeholder.style.display = 'block';

    if (hour >= 5 && hour < 12) {
      try {
        const data = await API.getDailyMessage('morning');
        if (data.available) {
          document.getElementById('morningGreeting').textContent = data.data.greeting || '';
          document.getElementById('morningAction').textContent = '今日小善举：' + (data.data.kind_action || '');
          morningCard.classList.add('visible');
          placeholder.style.display = 'none';
        }
      } catch (e) { /* ignore */ }
    } else if (hour >= 17 && hour < 23) {
      try {
        const data = await API.getDailyMessage('evening');
        if (data.available) {
          document.getElementById('eveningSummary').textContent = data.data.summary || '';
          eveningCard.classList.add('visible');
          placeholder.style.display = 'none';
        }
      } catch (e) { /* ignore */ }
    }
  }

  // ---- Stats ----
  async function updateStats() {
    try {
      const stats = await API.getStats();
      document.getElementById('streakBadge').textContent = `连续 ${stats.streak_days} 天`;
      document.getElementById('gardenTitle').textContent = stats.garden_level || '小萌芽花园';
      document.getElementById('gardenStats').textContent =
        `共 ${stats.total_flowers} 朵花 · 今日 ${stats.today_flowers} 朵`;
    } catch (e) { /* ignore */ }
  }

  // ---- Submit thought ----
  async function handleSubmit() {
    const content = input.value.trim();
    if (!content) return;

    submitBtn.disabled = true;
    tooth.setState('thinking');
    tooth.showBubble('嗯...让我想想...', false);

    try {
      const result = await API.submitThought(content);
      const { thought, flower } = result;

      tooth.setState(getAnimState(thought.emotion));
      tooth.showBubble(thought.ai_response, true);
      input.value = '';
      updateCharCount();

      await garden.refresh(flower.id);
      await updateStats();

      if (thought.emotion === 'happy' || thought.emotion === 'excited' || thought.emotion === 'grateful') {
        setTimeout(() => tooth.setState('idle'), 3000);
      }
    } catch (e) {
      showToast(e.message || '出错了，请稍后再试', true);
      tooth.setState('idle');
    } finally {
      submitBtn.disabled = false;
      input.focus();
    }
  }

  function getAnimState(emotion) {
    const map = {
      happy: 'celebrating',
      grateful: 'celebrating',
      excited: 'celebrating',
      hopeful: 'celebrating',
      calm: 'idle',
      worried: 'comforting',
      sad: 'comforting',
      anxious: 'comforting',
      confused: 'comforting',
      neutral: 'idle',
    };
    return map[emotion] || 'idle';
  }

  // ---- Char count ----
  function updateCharCount() {
    const len = input.value.length;
    charCount.textContent = len;
    if (len > 450) {
      charCount.style.color = 'var(--error-red)';
    } else {
      charCount.style.color = '';
    }
  }

  // ---- History drawer ----
  function createOverlay() {
    if (!overlay) {
      overlay = document.createElement('div');
      overlay.className = 'drawer-overlay';
      document.body.appendChild(overlay);
      overlay.addEventListener('click', closeDrawer);
    }
  }

  function openDrawer() {
    createOverlay();
    drawer.classList.add('open');
    overlay.classList.add('visible');
    loadHistory();
  }

  function closeDrawer() {
    drawer.classList.remove('open');
    if (overlay) overlay.classList.remove('visible');
  }

  async function loadHistory() {
    try {
      const data = await API.getThoughts(1, 50);
      if (!data.thoughts || data.thoughts.length === 0) {
        drawerList.innerHTML = '<p class="drawer-empty">还没有想法，快去写第一条吧~</p>';
        return;
      }
      drawerList.innerHTML = data.thoughts.map(t => `
        <div class="drawer-item" data-id="${t.id}">
          <div class="item-content">${escapeHtml(t.content)}</div>
          <div class="item-meta">
            <span>${t.emotion || ''}</span>
            <span>${(t.created_at || '').slice(0, 16)}</span>
          </div>
        </div>
      `).join('');

      drawerList.querySelectorAll('.drawer-item').forEach(item => {
        item.addEventListener('click', async () => {
          const id = item.dataset.id;
          try {
            const thought = await API.getThought(id);
            tooth.showBubble(thought.ai_response, true);
            closeDrawer();
          } catch (e) { /* ignore */ }
        });
      });
    } catch (e) {
      console.error('Load history error:', e);
    }
  }

  // ---- Toast ----
  let toastTimer = null;
  function showToast(msg, isError = false) {
    toast.textContent = msg;
    toast.className = 'toast' + (isError ? ' error' : '');
    toast.classList.add('show');
    if (toastTimer) clearTimeout(toastTimer);
    toastTimer = setTimeout(() => {
      toast.classList.remove('show');
    }, 2500);
  }

  function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
  }

  // ---- Events ----
  function bindEvents() {
    submitBtn.addEventListener('click', handleSubmit);
    input.addEventListener('input', updateCharCount);
    input.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
        e.preventDefault();
        handleSubmit();
      }
    });
    input.addEventListener('focus', () => {
      if (tooth.currentState === 'idle') {
        tooth.setState('listening');
      }
    });
    input.addEventListener('blur', () => {
      if (tooth.currentState === 'listening') {
        tooth.setState('idle');
      }
    });

    drawToggle.addEventListener('click', openDrawer);
    drawerClose.addEventListener('click', closeDrawer);
  }

  // ---- Start ----
  document.addEventListener('DOMContentLoaded', init);
})();
