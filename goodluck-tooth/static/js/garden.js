class GardenRenderer {
  constructor() {
    this.ground = document.getElementById('gardenGround');
    this.empty = document.getElementById('gardenEmpty');
    this.title = document.getElementById('gardenTitle');
    this.stats = document.getElementById('gardenStats');
    this.popover = document.getElementById('flowerPopover');
    this._initPopoverClose();
  }

  async refresh(newFlowerId = null) {
    try {
      const data = await API.getGarden();
      const statsData = await API.getGardenStats();
      this._updateHeader(statsData);
      this._renderFlowers(data.flowers, newFlowerId);
    } catch (e) {
      console.error('Garden refresh failed:', e);
    }
  }

  _updateHeader(statsData) {
    this.title.textContent = statsData.garden_level || '小萌芽花园';
    this.stats.textContent = `共 ${statsData.total_flowers} 朵花 · 今日 ${statsData.today_flowers} 朵`;
  }

  _renderFlowers(flowers, newFlowerId) {
    const existing = this.ground.querySelectorAll('.flower');
    existing.forEach(el => el.remove());

    if (!flowers || flowers.length === 0) {
      this.empty.style.display = 'block';
      return;
    }
    this.empty.style.display = 'none';

    flowers.forEach((f, index) => {
      const el = this._createFlowerEl(f, index, f.id === newFlowerId);
      this.ground.appendChild(el);
    });
  }

  _createFlowerEl(flower, index, isNew) {
    const el = document.createElement('div');
    el.className = `flower flower-${flower.flower_type} sway`;
    el.style.left = `${flower.position_x}%`;
    el.style.top = `${flower.position_y}%`;
    el.style.transform = `scale(${flower.size || 1})`;
    el.style.animationDelay = `${index * 50}ms`;
    el.style.setProperty('--sway-delay', `${(index % 5) * 0.3}s`);
    el.dataset.flowerId = flower.id;
    el.dataset.thoughtId = flower.thought_id || '';

    if (isNew) {
      el.classList.add('new-flower');
    }

    el.innerHTML = `
      <div class="flower-head">
        <div class="flower-petals">
          <div class="petal"></div><div class="petal"></div>
          <div class="petal"></div><div class="petal"></div>
          <div class="petal"></div><div class="petal"></div>
        </div>
        <div class="flower-center"></div>
      </div>
      <div class="flower-stem"></div>
    `;

    el.addEventListener('click', (e) => {
      e.stopPropagation();
      this._showPopover(flower, e);
    });

    return el;
  }

  async _showPopover(flower, event) {
    try {
      let thoughtData = null;
      if (flower.thought_id) {
        thoughtData = await API.getThought(flower.thought_id);
      }

      document.getElementById('popoverThought').textContent =
        thoughtData ? `"${thoughtData.content}"` : '这是一朵花园里的花';
      document.getElementById('popoverEmotion').textContent =
        thoughtData ? thoughtData.emotion || '' : '';
      document.getElementById('popoverResponse').textContent =
        thoughtData ? thoughtData.ai_response || '' : '';

      const time = flower.planted_at || (thoughtData && thoughtData.created_at) || '';
      document.getElementById('popoverTime').textContent = time ? `种于 ${time}` : '';

      const x = Math.min(event.clientX, window.innerWidth - 310);
      const y = Math.min(event.clientY - 160, window.innerHeight - 250);
      this.popover.style.left = `${Math.max(10, x)}px`;
      this.popover.style.top = `${Math.max(10, y)}px`;
      this.popover.classList.add('visible');

      setTimeout(() => {
        document.addEventListener('click', this._popoverClickOutside, { once: true });
      }, 0);
    } catch (e) {
      console.error('Popover error:', e);
    }
  }

  _initPopoverClose() {
    document.getElementById('popoverClose').addEventListener('click', (e) => {
      e.stopPropagation();
      this.popover.classList.remove('visible');
    });
  }

  _popoverClickOutside = (e) => {
    if (!this.popover.contains(e.target)) {
      this.popover.classList.remove('visible');
    }
  };
}
