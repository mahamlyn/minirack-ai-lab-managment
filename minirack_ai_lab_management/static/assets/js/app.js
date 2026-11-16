/*  Vue 3 Application */
const { createApp, ref, reactive, computed, onMounted, watch } = Vue;

// API service
class ApiService {
    constructor() {
        this.baseUrl = '/api/v1';
        this.timeout = 5000;
    }

    async fetch(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), this.timeout);

        try {
            const response = await fetch(url, {
                ...options,
                signal: controller.signal,
            });
            clearTimeout(timeoutId);

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            return await response.json();
        } catch (error) {
            clearTimeout(timeoutId);
            console.error('API Error:', error);
            throw error;
        }
    }

    async get(endpoint) {
        return this.fetch(endpoint, { method: 'GET' });
    }

    async post(endpoint, data) {
        return this.fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
        });
    }

    // Dashboard
    async getDashboard() {
        return this.get('/dashboard');
    }

    // Health
    async getHealth() {
        return this.get('/health');
    }

    // Configuration
    async getConfig() {
        return this.get('/config');
    }

    async updateConfig(service, setting, value) {
        return this.post('/config/update', { service, setting, value });
    }

    // Models
    async getModels() {
        return this.get('/models');
    }

    // Logs
    async getLogs(type = 'system', resource = 'laforge') {
        return this.get(`/logs/${type}/${resource}`);
    }
}

const api = new ApiService();

// Main application
const app = createApp({
    setup() {
        // State
        const dashboard = reactive({
            hosts: [],
            services: [],
            models: [],
            metrics: [],
            alerts: [],
            loading: true,
            error: null,
            lastUpdate: null,
        });

        const ui = reactive({
            currentPage: 'dashboard',
            sidebarOpen: true,
            darkMode: false,
            refreshInterval: 30000, // 30 seconds
        });

        const selectedHost = ref(null);
        const selectedService = ref(null);
        const logs = ref([]);
        const logsLoading = ref(false);

        // Computed properties
        const healthyHosts = computed(() =>
            dashboard.hosts.filter(h => h.status === 'healthy').length
        );

        const runningServices = computed(() =>
            dashboard.services.filter(s => s.status === 'running').length
        );

        const averageCPU = computed(() => {
            if (dashboard.hosts.length === 0) return 0;
            const sum = dashboard.hosts.reduce((acc, h) => acc + h.cpu_percent, 0);
            return (sum / dashboard.hosts.length).toFixed(1);
        });

        const averageMemory = computed(() => {
            if (dashboard.hosts.length === 0) return 0;
            const sum = dashboard.hosts.reduce((acc, h) => acc + h.memory_percent, 0);
            return (sum / dashboard.hosts.length).toFixed(1);
        });

        // Methods
        const refreshDashboard = async () => {
            try {
                dashboard.loading = true;
                dashboard.error = null;
                const data = await api.getDashboard();
                dashboard.hosts = data.hosts || [];
                dashboard.services = data.services || [];
                dashboard.models = data.models || [];
                dashboard.metrics = data.recent_metrics || [];
                dashboard.alerts = data.alerts || [];
                dashboard.lastUpdate = new Date();
            } catch (error) {
                dashboard.error = `Failed to load dashboard: ${error.message}`;
                console.error('Dashboard error:', error);
            } finally {
                dashboard.loading = false;
            }
        };

        const getStatusColor = (status) => {
            const colors = {
                healthy: '#10b981',
                warning: '#f59e0b',
                error: '#ef4444',
                offline: '#9ca3af',
                running: '#10b981',
                stopped: '#ef4444',
                unknown: '#9ca3af',
            };
            return colors[status] || colors.unknown;
        };

        const formatBytes = (bytes) => {
            if (bytes === 0) return '0 B';
            const k = 1024;
            const sizes = ['B', 'KB', 'MB', 'GB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
        };

        const formatUptime = (seconds) => {
            const days = Math.floor(seconds / 86400);
            const hours = Math.floor((seconds % 86400) / 3600);
            const minutes = Math.floor((seconds % 3600) / 60);

            if (days > 0) return `${days}d ${hours}h`;
            if (hours > 0) return `${hours}h ${minutes}m`;
            return `${minutes}m`;
        };

        const selectHost = async (host) => {
            selectedHost.value = host;
            logsLoading.value = true;
            try {
                logs.value = await api.getLogs('system', host.name.toLowerCase());
            } catch (error) {
                logs.value = [];
                console.error('Error fetching logs:', error);
            } finally {
                logsLoading.value = false;
            }
        };

        const toggleSidebar = () => {
            ui.sidebarOpen = !ui.sidebarOpen;
        };

        const toggleDarkMode = () => {
            ui.darkMode = !ui.darkMode;
            document.body.classList.toggle('dark-mode', ui.darkMode);
        };

        const navigateTo = (page) => {
            ui.currentPage = page;
            if (window.innerWidth <= 768) {
                ui.sidebarOpen = false;
            }
        };

        const getStatusIcon = (status) => {
            const icons = {
                healthy: '✓',
                warning: '⚠',
                error: '✕',
                offline: '○',
            };
            return icons[status] || '?';
        };

        // Lifecycle
        onMounted(() => {
            refreshDashboard();
            const interval = setInterval(refreshDashboard, ui.refreshInterval);
            return () => clearInterval(interval);
        });

        // Auto-detect dark mode
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        ui.darkMode = prefersDark;
        document.body.classList.toggle('dark-mode', ui.darkMode);

        return {
            dashboard,
            ui,
            selectedHost,
            selectedService,
            logs,
            logsLoading,
            healthyHosts,
            runningServices,
            averageCPU,
            averageMemory,
            refreshDashboard,
            getStatusColor,
            formatBytes,
            formatUptime,
            selectHost,
            toggleSidebar,
            toggleDarkMode,
            navigateTo,
            getStatusIcon,
        };
    },

    template: `
        <div class="app-layout" :class="{ 'sidebar-closed': !ui.sidebarOpen }">
            <!-- Sidebar -->
            <aside class="sidebar" :class="{ open: ui.sidebarOpen }">
                <a href="#" class="logo" @click.prevent="navigateTo('dashboard')">
                    <div class="logo-icon">⚡</div>
                    <span>MiniRack</span>
                </a>

                <!-- Navigation -->
                <nav class="nav-section">
                    <div class="nav-section-title">Main</div>
                    <a href="#" class="nav-item" :class="{ active: ui.currentPage === 'dashboard' }"
                       @click.prevent="navigateTo('dashboard')">
                        <span class="icon-dashboard"></span>
                        <span>Dashboard</span>
                    </a>
                    <a href="#" class="nav-item" :class="{ active: ui.currentPage === 'hosts' }"
                       @click.prevent="navigateTo('hosts')">
                        <span class="icon-hosts"></span>
                        <span>Hosts</span>
                    </a>
                    <a href="#" class="nav-item" :class="{ active: ui.currentPage === 'services' }"
                       @click.prevent="navigateTo('services')">
                        <span class="icon-services"></span>
                        <span>Services</span>
                    </a>
                </nav>

                <nav class="nav-section">
                    <div class="nav-section-title">AI</div>
                    <a href="#" class="nav-item" :class="{ active: ui.currentPage === 'models' }"
                       @click.prevent="navigateTo('models')">
                        <span class="icon-models"></span>
                        <span>Models</span>
                    </a>
                    <a href="#" class="nav-item" :class="{ active: ui.currentPage === 'logs' }"
                       @click.prevent="navigateTo('logs')">
                        <span class="icon-logs"></span>
                        <span>Logs</span>
                    </a>
                </nav>

                <nav class="nav-section">
                    <div class="nav-section-title">System</div>
                    <a href="#" class="nav-item" :class="{ active: ui.currentPage === 'config' }"
                       @click.prevent="navigateTo('config')">
                        <span class="icon-config"></span>
                        <span>Configuration</span>
                    </a>
                </nav>
            </aside>

            <!-- Main content -->
            <div class="main-content">
                <!-- Top bar -->
                <header class="topbar">
                    <div class="topbar-left">
                        <button class="btn btn-secondary btn-xs" @click="toggleSidebar">
                            <span class="icon-menu"></span>
                        </button>
                        <div class="topbar-title">{{ ui.currentPage | capitalize }}</div>
                    </div>
                    <div class="topbar-right">
                        <span v-if="dashboard.lastUpdate" class="text-secondary" style="font-size: 0.875rem;">
                            Updated: {{ dashboard.lastUpdate | formatTime }}
                        </span>
                        <button class="btn btn-secondary btn-xs" @click="toggleDarkMode" title="Toggle dark mode">
                            {{ ui.darkMode ? '☀️' : '🌙' }}
                        </button>
                        <button class="btn btn-secondary btn-xs" @click="refreshDashboard" title="Refresh">
                            <span class="icon-refresh"></span>
                        </button>
                    </div>
                </header>

                <!-- Content area -->
                <div class="content-area">
                    <!-- Loading state -->
                    <div v-if="dashboard.loading" class="loading-screen">
                        <div class="loader"></div>
                        <p>Loading dashboard...</p>
                    </div>

                    <!-- Error alerts -->
                    <div v-if="dashboard.error" class="alert alert-error">
                        <span class="alert-icon">⚠</span>
                        <div>{{ dashboard.error }}</div>
                    </div>

                    <!-- Dashboard Page -->
                    <div v-if="ui.currentPage === 'dashboard'">
                        <!-- Summary cards -->
                        <div class="grid grid-4" style="margin-bottom: 2rem;">
                            <div class="card">
                                <div class="card-title">Healthy Hosts</div>
                                <div style="font-size: 2rem; font-weight: 700; color: var(--primary);">
                                    {{ healthyHosts }}/{{ dashboard.hosts.length }}
                                </div>
                            </div>
                            <div class="card">
                                <div class="card-title">Services Running</div>
                                <div style="font-size: 2rem; font-weight: 700; color: var(--success);">
                                    {{ runningServices }}/{{ dashboard.services.length }}
                                </div>
                            </div>
                            <div class="card">
                                <div class="card-title">Avg CPU</div>
                                <div style="font-size: 2rem; font-weight: 700; color: var(--warning);">
                                    {{ averageCPU }}%
                                </div>
                            </div>
                            <div class="card">
                                <div class="card-title">Avg Memory</div>
                                <div style="font-size: 2rem; font-weight: 700; color: var(--info);">
                                    {{ averageMemory }}%
                                </div>
                            </div>
                        </div>

                        <!-- Hosts grid -->
                        <div style="margin-bottom: 2rem;">
                            <h2 style="font-size: 1.5rem; font-weight: 700; margin-bottom: 1rem;">Hosts</h2>
                            <div class="grid grid-3">
                                <div v-for="host in dashboard.hosts" :key="host.name" class="card host-card">
                                    <div class="host-header">
                                        <div>
                                            <div class="host-name">{{ host.name }}</div>
                                            <span class="status-badge" :class="host.status">
                                                <span class="status-dot" :class="host.status"></span>
                                                {{ host.status }}
                                            </span>
                                        </div>
                                        <div class="host-role">{{ host.role }}</div>
                                    </div>

                                    <div class="host-metrics">
                                        <div class="metric">
                                            <span class="metric-label">
                                                <span class="icon-cpu"></span> CPU
                                            </span>
                                            <span class="metric-value">{{ host.cpu_percent.toFixed(1) }}%</span>
                                        </div>
                                        <div class="metric-bar">
                                            <div class="metric-bar-fill" :style="{ width: host.cpu_percent + '%' }"></div>
                                        </div>

                                        <div class="metric">
                                            <span class="metric-label">
                                                <span class="icon-memory"></span> Memory
                                            </span>
                                            <span class="metric-value">{{ host.memory_percent.toFixed(1) }}%</span>
                                        </div>
                                        <div class="metric-bar">
                                            <div class="metric-bar-fill" :style="{ width: host.memory_percent + '%' }"></div>
                                        </div>

                                        <div class="metric">
                                            <span class="metric-label">
                                                <span class="icon-disk"></span> Disk
                                            </span>
                                            <span class="metric-value">{{ host.disk_percent.toFixed(1) }}%</span>
                                        </div>
                                        <div class="metric-bar">
                                            <div class="metric-bar-fill" :style="{ width: host.disk_percent + '%' }"></div>
                                        </div>

                                        <div class="metric">
                                            <span class="metric-label">⬆️ Uptime</span>
                                            <span class="metric-value">{{ formatUptime(host.uptime_seconds) }}</span>
                                        </div>

                                        <div class="metric">
                                            <span class="metric-label">🔗 IP</span>
                                            <span class="metric-value" style="font-family: monospace; font-size: 0.875rem;">
                                                {{ host.ip_address }}
                                            </span>
                                        </div>
                                    </div>

                                    <button class="btn btn-primary" style="width: 100%; justify-content: center;"
                                            @click="selectHost(host)">
                                        View Details
                                    </button>
                                </div>
                            </div>
                        </div>

                        <!-- Services -->
                        <div>
                            <h2 style="font-size: 1.5rem; font-weight: 700; margin-bottom: 1rem;">Services</h2>
                            <div class="card">
                                <div class="services-list">
                                    <div v-for="service in dashboard.services" :key="service.name" class="service-item">
                                        <div class="service-info">
                                            <div class="service-name">{{ service.name }}</div>
                                            <div class="service-host">{{ service.host }}</div>
                                        </div>
                                        <span class="status-badge" :class="service.status">
                                            <span class="status-dot" :class="service.status"></span>
                                            {{ service.status }}
                                        </span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Hosts Page -->
                    <div v-if="ui.currentPage === 'hosts'">
                        <div class="grid grid-2">
                            <div v-for="host in dashboard.hosts" :key="host.name" class="card fade-in">
                                <div class="card-title">{{ host.name }}</div>
                                <div style="display: grid; gap: 1rem;">
                                    <div>
                                        <div style="font-size: 0.875rem; color: var(--text-secondary); margin-bottom: 0.5rem;">
                                            Status: {{ host.status | capitalize }}
                                        </div>
                                        <span class="status-badge" :class="host.status">
                                            <span class="status-dot" :class="host.status"></span>
                                            {{ host.status }}
                                        </span>
                                    </div>
                                    <div>IP Address: <code style="background: var(--light); padding: 0.25rem 0.5rem; border-radius: 4px;">{{ host.ip_address }}</code></div>
                                    <div>Role: <strong>{{ host.role }}</strong></div>
                                    <div>Uptime: {{ formatUptime(host.uptime_seconds) }}</div>
                                    <div>CPU: {{ host.cpu_percent.toFixed(1) }}%</div>
                                    <div>Memory: {{ host.memory_percent.toFixed(1) }}%</div>
                                    <div>Disk: {{ host.disk_percent.toFixed(1) }}%</div>
                                    <div v-if="host.temperature_celsius">Temperature: {{ host.temperature_celsius.toFixed(1) }}°C</div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Services Page -->
                    <div v-if="ui.currentPage === 'services'">
                        <div class="card">
                            <div class="card-title">System Services</div>
                            <div class="services-list">
                                <div v-for="service in dashboard.services" :key="service.name" class="service-item">
                                    <div>
                                        <div class="service-name">{{ service.name }}</div>
                                        <div class="service-host">{{ service.host }}</div>
                                    </div>
                                    <span class="status-badge" :class="service.status">
                                        {{ service.status }}
                                    </span>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Models Page -->
                    <div v-if="ui.currentPage === 'models'">
                        <div class="card">
                            <div class="card-title">AI Models</div>
                            <div v-if="dashboard.models.length === 0" class="alert alert-info">
                                <span class="alert-icon">ℹ</span>
                                <div>No models currently available. Check Ollama service on ai-core.</div>
                            </div>
                            <div v-else class="models-grid">
                                <div v-for="model in dashboard.models" :key="model.name" class="model-card">
                                    <div class="model-name">{{ model.name }}</div>
                                    <div class="model-size">{{ formatBytes(model.size_gb * 1e9) }}</div>
                                    <div class="model-actions">
                                        <button class="btn btn-sm btn-primary">Use</button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Logs Page -->
                    <div v-if="ui.currentPage === 'logs'">
                        <div class="card">
                            <div class="card-title">System Logs</div>
                            <div v-if="logsLoading" style="text-align: center; padding: 2rem;">
                                <div class="loader"></div>
                            </div>
                            <div v-else-if="logs.length === 0" class="alert alert-info">
                                <span class="alert-icon">ℹ</span>
                                <div>No logs available. Select a host from the dashboard to view logs.</div>
                            </div>
                            <div v-else style="overflow-x: auto;">
                                <pre style="background: var(--light); padding: 1rem; border-radius: var(--radius-md); overflow-x: auto; max-height: 500px; overflow-y: auto;"><code v-for="(log, idx) in logs.slice(0, 50)" :key="idx">{{ log }}
</code></pre>
                            </div>
                        </div>
                    </div>

                    <!-- Configuration Page -->
                    <div v-if="ui.currentPage === 'config'">
                        <div class="card">
                            <div class="card-title">Configuration</div>
                            <div style="display: grid; gap: 1.5rem;">
                                <div>
                                    <label style="display: block; margin-bottom: 0.5rem; font-weight: 600;">
                                        Ollama Model
                                    </label>
                                    <select style="width: 100%; padding: 0.75rem; border: 1px solid var(--border-color); border-radius: var(--radius-md);">
                                        <option>llama3.2</option>
                                        <option>mistral</option>
                                        <option>llama2</option>
                                        <option>neural-chat</option>
                                    </select>
                                </div>
                                <div>
                                    <label style="display: block; margin-bottom: 0.5rem; font-weight: 600;">
                                        Ollama Host Binding
                                    </label>
                                    <input type="text" value="0.0.0.0:11434" style="width: 100%; padding: 0.75rem; border: 1px solid var(--border-color); border-radius: var(--radius-md);" />
                                </div>
                                <button class="btn btn-primary">Save Configuration</button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `,
});

// Filters
app.config.globalProperties.$filters = {
    capitalize: (value) => {
        if (!value) return '';
        value = value.toString();
        return value.charAt(0).toUpperCase() + value.slice(1);
    },
    formatTime: (date) => {
        if (!date) return '';
        return new Date(date).toLocaleTimeString();
    },
};

// Mount app
app.mount('#app');
