def __init__(self) -> None:
    super().__init__()
    self.setObjectName("DashboardRoot")

    self._last_update_ts: Optional[float] = None
    self._cpu_hist: Deque[float] = deque(maxlen=CFG.history_len)
    self._ram_hist: Deque[float] = deque(maxlen=CFG.history_len)
    self._disk_hist: Deque[float] = deque(maxlen=CFG.history_len)
    self._net_hist: Deque[float] = deque(maxlen=CFG.history_len)

    root = QVBoxLayout(self)
    root.setContentsMargins(16, 16, 16, 16)
    root.setSpacing(CFG.gap)

    # ==========================
    # HERO
    # ==========================
    self.hero = HoverCard()

    hero_row = QHBoxLayout()
    hero_row.setContentsMargins(0, 0, 0, 0)
    hero_row.setSpacing(14)

    self.health_big = QLabel("🟢 System Stable")
    self.health_big.setObjectName("TitleXL")

    self.health_hint = QLabel("No recent anomalies. Collect data to begin monitoring.")
    self.health_hint.setObjectName("Muted")

    self.last_update = QLabel("Last update: —")
    self.last_update.setObjectName("Muted")

    left = QVBoxLayout()
    left.setSpacing(4)
    left.addWidget(self.health_big)
    left.addWidget(self.health_hint)
    left.addWidget(self.last_update)

    hero_row.addLayout(left, 1)

    pills = QVBoxLayout()
    pills.setSpacing(8)
    pills.setAlignment(Qt.AlignRight | Qt.AlignTop)

    self.p_live = Pill("Live: OFF", "neutral")
    self.p_model = Pill("Model: —", "neutral")
    self.p_data = Pill("Data: —", "neutral")
    self.p_window = Pill(f"Window: last {CFG.history_len}", "neutral")

    pills.addWidget(self.p_live)
    pills.addWidget(self.p_model)
    pills.addWidget(self.p_data)
    pills.addWidget(self.p_window)

    hero_row.addLayout(pills)
    self.hero.lay.addLayout(hero_row)
    root.addWidget(self.hero)

    # ==========================
    # KPI GRID (2x2 for small screens)
    # ==========================
    kpi_wrap = QWidget()
    kpi = QGridLayout(kpi_wrap)
    kpi.setContentsMargins(0, 0, 0, 0)
    kpi.setHorizontalSpacing(CFG.gap)
    kpi.setVerticalSpacing(CFG.gap)

    self.k_cpu = KpiCard("CPU", "🧠")
    self.k_ram = KpiCard("RAM", "💾")
    self.k_disk = KpiCard("Disk", "🗄️")
    self.k_net = KpiCard("Network", "📡")

    kpi.addWidget(self.k_cpu, 0, 0)
    kpi.addWidget(self.k_ram, 0, 1)
    kpi.addWidget(self.k_disk, 1, 0)
    kpi.addWidget(self.k_net, 1, 1)

    kpi.setColumnStretch(0, 1)
    kpi.setColumnStretch(1, 1)

    root.addWidget(kpi_wrap)

    # ==========================
    # TRENDS (full width)
    # ==========================
    self.trends = HoverCard()

    trends_header = QHBoxLayout()
    trends_header.setContentsMargins(0, 0, 0, 0)
    trends_header.setSpacing(10)

    t_title = QLabel("Trends")
    t_title.setObjectName("SectionTitle")
    t_sub = QLabel("CPU / RAM / Disk / Net history (live sparklines).")
    t_sub.setObjectName("Muted")

    left_hdr = QVBoxLayout()
    left_hdr.setSpacing(2)
    left_hdr.addWidget(t_title)
    left_hdr.addWidget(t_sub)

    trends_header.addLayout(left_hdr, 1)

    self.trends_state = Pill("Waiting for data", "neutral")
    trends_header.addWidget(self.trends_state)

    self.trends.lay.addLayout(trends_header)

    tiles_wrap = QWidget()
    tiles = QGridLayout(tiles_wrap)
    tiles.setContentsMargins(0, 0, 0, 0)
    tiles.setHorizontalSpacing(CFG.gap)
    tiles.setVerticalSpacing(CFG.gap)

    self.tile_cpu = ChartTile("CPU %", "recent window")
    self.tile_ram = ChartTile("RAM %", "recent window")
    self.tile_disk = ChartTile("Disk %", "recent window")
    self.tile_net = ChartTile("Net KB/s", "recent window")

    tiles.addWidget(self.tile_cpu, 0, 0)
    tiles.addWidget(self.tile_ram, 0, 1)
    tiles.addWidget(self.tile_disk, 1, 0)
    tiles.addWidget(self.tile_net, 1, 1)

    tiles.setColumnStretch(0, 1)
    tiles.setColumnStretch(1, 1)
    tiles.setRowStretch(0, 1)
    tiles.setRowStretch(1, 1)

    self.trends.lay.addWidget(tiles_wrap, 1)

    root.addWidget(self.trends, 1)

    # ==========================
    # Initial state + tick
    # ==========================
    self.set_status_badges(live=False, model_ok=False, data_ok=False)
    self._update_all(cpu=None, ram=None, disk=None, net_kbps=None)

    self._ticker = QTimer(self)
    self._ticker.setInterval(800)
    self._ticker.timeout.connect(self._refresh_last_update_label)
    self._ticker.start()
