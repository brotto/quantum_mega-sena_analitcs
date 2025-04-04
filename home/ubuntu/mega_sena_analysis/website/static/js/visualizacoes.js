// visualizacoes.js - Visualizações avançadas para o MegaSenaPredictor

// Configurações globais para Chart.js
Chart.defaults.font.family = "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif";
Chart.defaults.color = '#555';
Chart.defaults.plugins.tooltip.backgroundColor = 'rgba(0, 0, 0, 0.7)';
Chart.defaults.plugins.tooltip.padding = 10;
Chart.defaults.plugins.tooltip.cornerRadius = 5;
Chart.defaults.plugins.legend.labels.usePointStyle = true;

// Paleta de cores personalizada
const CORES_PRIMARIAS = [
    '#0d6efd', '#6610f2', '#6f42c1', '#d63384', '#dc3545', 
    '#fd7e14', '#ffc107', '#198754', '#20c997', '#0dcaf0'
];

const CORES_SECUNDARIAS = [
    '#cfe2ff', '#e0cffc', '#d8c6f7', '#f5c2d6', '#f8d7da',
    '#fff3cd', '#fff3cd', '#d1e7dd', '#d2f4ea', '#cff4fc'
];

// Classe para gerenciar visualizações avançadas
class VisualizacoesMegaSena {
    constructor() {
        this.graficos = {};
        this.dados = {
            estatisticas: null,
            raizes: null,
            previsoes: null,
            validacao: null
        };
    }

    // Inicializar visualizações
    inicializar() {
        // Adicionar event listeners para tabs de visualização
        document.querySelectorAll('.nav-link[data-bs-toggle="tab"]').forEach(tab => {
            tab.addEventListener('shown.bs.tab', event => {
                const targetId = event.target.getAttribute('href');
                this.redimensionarGraficos(targetId);
            });
        });

        // Adicionar event listener para redimensionamento da janela
        window.addEventListener('resize', () => {
            this.redimensionarGraficos();
        });
    }

    // Redimensionar gráficos quando necessário
    redimensionarGraficos(containerId = null) {
        if (containerId) {
            // Redimensionar apenas os gráficos no container especificado
            Object.keys(this.graficos).forEach(key => {
                if (document.getElementById(key).closest(containerId)) {
                    if (this.graficos[key]) {
                        this.graficos[key].resize();
                    }
                }
            });
        } else {
            // Redimensionar todos os gráficos
            Object.values(this.graficos).forEach(grafico => {
                if (grafico) {
                    grafico.resize();
                }
            });
        }
    }

    // Visualizações para estatísticas
    visualizarEstatisticas(dados) {
        this.dados.estatisticas = dados;
        
        // Criar gráfico de frequência interativo
        this.criarGraficoFrequencia('graficoFrequenciaInterativo', dados);
        
        // Criar gráfico de calor para números
        this.criarMapaCalorNumeros('mapaCalorNumeros', dados);
        
        // Criar gráfico de tendências temporais
        this.criarGraficoTendencias('graficoTendencias', dados);
    }

    // Criar gráfico de frequência interativo
    criarGraficoFrequencia(elementId, dados) {
        const container = document.getElementById(elementId);
        if (!container) return;
        
        // Preparar dados
        const numeros = Array.from({length: 60}, (_, i) => i + 1);
        const frequencias = numeros.map(num => {
            const encontrado = dados.mais_frequentes.find(item => item[0] === num);
            if (encontrado) return encontrado[1];
            
            const encontradoMenos = dados.menos_frequentes.find(item => item[0] === num);
            if (encontradoMenos) return encontradoMenos[1];
            
            // Estimar valor intermediário
            return Math.floor((dados.mais_frequentes[dados.mais_frequentes.length - 1][1] + 
                              dados.menos_frequentes[0][1]) / 2);
        });
        
        // Calcular média e desvio padrão
        const media = frequencias.reduce((a, b) => a + b, 0) / frequencias.length;
        const desvioPadrao = Math.sqrt(
            frequencias.map(x => Math.pow(x - media, 2)).reduce((a, b) => a + b, 0) / frequencias.length
        );
        
        // Determinar cores baseadas no desvio da média
        const cores = frequencias.map(freq => {
            const desvios = (freq - media) / desvioPadrao;
            if (desvios > 1.5) return '#198754'; // Muito acima da média
            if (desvios > 0.5) return '#0d6efd'; // Acima da média
            if (desvios < -1.5) return '#dc3545'; // Muito abaixo da média
            if (desvios < -0.5) return '#ffc107'; // Abaixo da média
            return '#6c757d'; // Próximo da média
        });
        
        // Criar gráfico
        const ctx = document.createElement('canvas');
        container.appendChild(ctx);
        
        this.graficos[elementId] = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: numeros,
                datasets: [{
                    label: 'Frequência',
                    data: frequencias,
                    backgroundColor: cores,
                    borderColor: cores.map(cor => cor.replace('0.8', '1')),
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    tooltip: {
                        callbacks: {
                            title: function(tooltipItems) {
                                return `Número ${tooltipItems[0].label}`;
                            },
                            label: function(context) {
                                const freq = context.raw;
                                const percentual = (freq / dados.total_sorteios / 6 * 100).toFixed(2);
                                return [
                                    `Frequência: ${freq} vezes`,
                                    `Percentual: ${percentual}%`,
                                    `Desvio da média: ${((freq - media) / desvioPadrao).toFixed(2)} σ`
                                ];
                            }
                        }
                    },
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Frequência'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Número'
                        }
                    }
                }
            }
        });
        
        // Adicionar legenda personalizada
        const legenda = document.createElement('div');
        legenda.className = 'mt-3 d-flex justify-content-center flex-wrap';
        legenda.innerHTML = `
            <div class="d-flex align-items-center me-3 mb-2">
                <div style="width: 15px; height: 15px; background-color: #198754; margin-right: 5px;"></div>
                <span>Muito acima da média (>1.5σ)</span>
            </div>
            <div class="d-flex align-items-center me-3 mb-2">
                <div style="width: 15px; height: 15px; background-color: #0d6efd; margin-right: 5px;"></div>
                <span>Acima da média (0.5-1.5σ)</span>
            </div>
            <div class="d-flex align-items-center me-3 mb-2">
                <div style="width: 15px; height: 15px; background-color: #6c757d; margin-right: 5px;"></div>
                <span>Próximo da média (±0.5σ)</span>
            </div>
            <div class="d-flex align-items-center me-3 mb-2">
                <div style="width: 15px; height: 15px; background-color: #ffc107; margin-right: 5px;"></div>
                <span>Abaixo da média (-0.5 a -1.5σ)</span>
            </div>
            <div class="d-flex align-items-center mb-2">
                <div style="width: 15px; height: 15px; background-color: #dc3545; margin-right: 5px;"></div>
                <span>Muito abaixo da média (<-1.5σ)</span>
            </div>
        `;
        container.appendChild(legenda);
    }

    // Criar mapa de calor para números
    criarMapaCalorNumeros(elementId, dados) {
        const container = document.getElementById(elementId);
        if (!container) return;
        
        // Preparar dados para o mapa de calor (matriz 6x10)
        const matrizCalor = [];
        for (let i = 0; i < 6; i++) {
            const linha = [];
            for (let j = 0; j < 10; j++) {
                const numero = i * 10 + j + 1;
                if (numero <= 60) {
                    // Encontrar frequência
                    const encontrado = dados.mais_frequentes.find(item => item[0] === numero);
                    if (encontrado) {
                        linha.push(encontrado[1]);
                    } else {
                        const encontradoMenos = dados.menos_frequentes.find(item => item[0] === numero);
                        if (encontradoMenos) {
                            linha.push(encontradoMenos[1]);
                        } else {
                            // Estimar valor intermediário
                            linha.push(Math.floor((dados.mais_frequentes[dados.mais_frequentes.length - 1][1] + 
                                                dados.menos_frequentes[0][1]) / 2));
                        }
                    }
                } else {
                    linha.push(null); // Valor nulo para números > 60
                }
            }
            matrizCalor.push(linha);
        }
        
        // Criar elemento para o mapa de calor
        const heatmapContainer = document.createElement('div');
        heatmapContainer.style.display = 'grid';
        heatmapContainer.style.gridTemplateColumns = 'repeat(10, 1fr)';
        heatmapContainer.style.gap = '4px';
        heatmapContainer.style.marginTop = '20px';
        
        // Encontrar valores mínimo e máximo para normalização
        const valoresValidos = matrizCalor.flat().filter(v => v !== null);
        const minValor = Math.min(...valoresValidos);
        const maxValor = Math.max(...valoresValidos);
        
        // Criar células do mapa de calor
        for (let i = 0; i < 6; i++) {
            for (let j = 0; j < 10; j++) {
                const numero = i * 10 + j + 1;
                if (numero <= 60) {
                    const valor = matrizCalor[i][j];
                    
                    // Normalizar valor para obter cor
                    const normalizado = (valor - minValor) / (maxValor - minValor);
                    
                    // Gerar cor (verde para alta frequência, vermelho para baixa)
                    const r = Math.floor(255 * (1 - normalizado));
                    const g = Math.floor(255 * normalizado);
                    const b = 0;
                    
                    const celula = document.createElement('div');
                    celula.className = 'numero-bola';
                    celula.style.backgroundColor = `rgb(${r}, ${g}, ${b})`;
                    celula.style.color = normalizado > 0.5 ? '#000' : '#fff';
                    celula.style.width = '100%';
                    celula.style.height = '40px';
                    celula.style.margin = '0';
                    celula.style.display = 'flex';
                    celula.style.alignItems = 'center';
                    celula.style.justifyContent = 'center';
                    celula.style.position = 'relative';
                    celula.textContent = numero;
                    
                    // Adicionar tooltip
                    celula.setAttribute('data-bs-toggle', 'tooltip');
                    celula.setAttribute('data-bs-placement', 'top');
                    celula.setAttribute('title', `Frequência: ${valor} vezes`);
                    
                    heatmapContainer.appendChild(celula);
                } else {
                    // Célula vazia para números > 60
                    const celula = document.createElement('div');
                    celula.style.width = '100%';
                    celula.style.height = '40px';
                    heatmapContainer.appendChild(celula);
                }
            }
        }
        
        container.appendChild(heatmapContainer);
        
        // Inicializar tooltips
        const tooltips = [].slice.call(container.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltips.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
        
        // Adicionar legenda
        const legenda = document.createElement('div');
        legenda.className = 'mt-3 d-flex justify-content-center align-items-center';
        legenda.innerHTML = `
            <div style="width: 200px; height: 20px; background: linear-gradient(to right, rgb(255, 0, 0), rgb(255, 255, 0), rgb(0, 255, 0)); margin: 0 10px;"></div>
            <div class="d-flex justify-content-between" style="width: 200px;">
                <span>Menos frequente</span>
                <span>Mais frequente</span>
            </div>
        `;
        container.appendChild(legenda);
    }

    // Criar gráfico de tendências temporais
    criarGraficoTendencias(elementId, dados) {
        // Esta função seria implementada com dados reais de tendências temporais
        // Como não temos esses dados específicos no objeto de estatísticas,
        // esta é uma implementação simulada
        
        const container = document.getElementById(elementId);
        if (!container) return;
        
        // Criar elemento para o gráfico
        const canvas = document.createElement('canvas');
        container.appendChild(canvas);
        
        // Simular dados de tendências temporais
        // Em uma implementação real, esses dados viriam do backend
        const periodos = 10;
        const labels = Array.from({length: periodos}, (_, i) => `Período ${i+1}`);
        
        // Simular tendências para diferentes métricas
        const datasetsSoma = {
            label: 'Soma dos números',
            data: Array.from({length: periodos}, () => Math.floor(Math.random() * 50) + 150),
            borderColor: CORES_PRIMARIAS[0],
            backgroundColor: CORES_SECUNDARIAS[0],
            tension: 0.4
        };
        
        const datasetsPares = {
            label: 'Números pares',
            data: Array.from({length: periodos}, () => Math.floor(Math.random() * 2) + 2),
            borderColor: CORES_PRIMARIAS[1],
            backgroundColor: CORES_SECUNDARIAS[1],
            tension: 0.4
        };
        
        const datasetsConsecutivos = {
            label: 'Números consecutivos',
            data: Array.from({length: periodos}, () => Math.floor(Math.random() * 3)),
            borderColor: CORES_PRIMARIAS[2],
            backgroundColor: CORES_SECUNDARIAS[2],
            tension: 0.4
        };
        
        // Criar gráfico
        this.graficos[elementId] = new Chart(canvas, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [datasetsSoma, datasetsPares, datasetsConsecutivos]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Tendências Temporais (Simulação)'
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false
                    },
                    legend: {
                        position: 'bottom'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: false,
                        title: {
                            display: tru
(Content truncated due to size limit. Use line ranges to read in chunks)