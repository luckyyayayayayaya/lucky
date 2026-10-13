class ToothAnimator {
  constructor() {
    this.container = document.getElementById('toothContainer');
    this.bubble = document.getElementById('speechBubble');
    this.bubbleText = document.getElementById('bubbleText');
    this.currentState = 'idle';
    this.typingTimer = null;
    this._initEyeTracking();
  }

  setState(state) {
    const states = ['idle', 'listening', 'thinking', 'celebrating', 'comforting', 'sleeping'];
    this.container.classList.remove(...states.map(s => `state-${s}`));
    this.container.classList.add(`state-${state}`);
    this.currentState = state;

    if (state === 'celebrating') {
      this._spawnSparkles();
    }
  }

  showBubble(text, animate = true) {
    this.bubbleText.textContent = '';
    this.bubble.classList.add('visible');
    if (animate) {
      this._typeText(text);
    } else {
      this.bubbleText.textContent = text;
    }
  }

  hideBubble() {
    this.bubble.classList.remove('visible');
    if (this.typingTimer) {
      clearInterval(this.typingTimer);
      this.typingTimer = null;
    }
  }

  _typeText(text) {
    if (this.typingTimer) clearInterval(this.typingTimer);
    let i = 0;
    this.bubbleText.textContent = '';
    this.typingTimer = setInterval(() => {
      if (i < text.length) {
        this.bubbleText.textContent += text[i];
        i++;
      } else {
        clearInterval(this.typingTimer);
        this.typingTimer = null;
      }
    }, 40);
  }

  _spawnSparkles() {
    const body = this.container.querySelector('.tooth-body');
    const rect = body.getBoundingClientRect();
    const cx = rect.left + rect.width / 2;
    const cy = rect.top + rect.height / 2;
    for (let i = 0; i < 10; i++) {
      const sparkle = document.createElement('div');
      sparkle.className = 'sparkle';
      const angle = Math.random() * Math.PI * 2;
      const distance = 30 + Math.random() * 50;
      sparkle.style.setProperty('--dx', `${Math.cos(angle) * distance}px`);
      sparkle.style.setProperty('--dy', `${Math.sin(angle) * distance}px`);
      sparkle.style.left = `${cx}px`;
      sparkle.style.top = `${cy}px`;
      sparkle.style.animationDuration = `${0.8 + Math.random() * 0.6}s`;
      sparkle.addEventListener('animationend', () => sparkle.remove());
      document.body.appendChild(sparkle);
    }
  }

  _initEyeTracking() {
    const pupils = this.container.querySelectorAll('.pupil');
    document.addEventListener('mousemove', (e) => {
      if (this.currentState === 'sleeping') return;
      const body = this.container.querySelector('.tooth-body');
      const rect = body.getBoundingClientRect();
      const cx = rect.left + rect.width / 2;
      const cy = rect.top + rect.height * 0.38;
      const dx = Math.max(-3, Math.min(3, (e.clientX - cx) / rect.width * 8));
      const dy = Math.max(-3, Math.min(3, (e.clientY - cy) / rect.height * 8));
      pupils.forEach(p => {
        p.style.transform = `translate(${dx}px, ${dy}px)`;
      });
    });
  }
}
