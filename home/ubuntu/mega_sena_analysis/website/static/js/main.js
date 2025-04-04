// main.js - Funcionalidades JavaScript para o MegaSenaPredictor

document.addEventListener('DOMContentLoaded', function() {
    // Inicialização
    verificarStatusDados();
    
    // Event Listeners
    document.getElementById('btnCarregarDados').addEventListener('click', carregarDados);
    document.getElementById('btnBaixarDados').addEventListener('click', baixarDados);
    document.getElementById('formAdicionarSorteio').addEventListener('submit', adicionarSorteio);
    document.getElementById('formDetectarRaizes').addEventListener('submit', detectarRaizes);
    document.getElementById('formGerarPrevisoes').addEventListener('submit', gerarPrevisoes);
    document.getElementById('formValidar').addEventListener('submit', validarModelo);
    
    // Ativar scrollspy para navegação
    const scrollSpy = new bootstrap.ScrollSpy(document.body, {
        target: '#navbarNav'
    });
    
    // Navegação suave para links internos
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                window.scrollTo({
                    top: targetElement.offsetTop - 70,
                    behavior: 'smooth'
                });
            }
        });
    });
});

// Funções de utilidade
function mostrarAlerta(mensagem, tipo = 'info') {
    const alertContainer = document.getElementById('alertContainer');
    const alertElement = document.createElement('div');
    alertElement.className = `alert alert-${tipo} alert-dismissible fade show`;
    alertElement.innerHTML = `
        ${mensagem}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Fechar"></button>
    `;
    alertContainer.appendChild(alertElement);
    
    // Auto-remover após 5 segundos
    setTimeout(() => {
        alertElement.classList.remove('show');
        setTimeout(() => alertElement.remove(), 500);
    }, 5000);
}

function criarBolasNumeros(numeros, tamanho = '') {
    let html = '';
    for (const numero of numeros) {
        html += `<div class="numero-bola ${tamanho}">${numero}</div>`;
    }
    return html;
}

// Funções de API
async function verificarStatusDados() {
    try {
        const response = await fetch('/api/dados/carregar');
        const data = await response.json();
        
        const statusDados = document.getElementById('statusDados');
        
        if (data.sucesso) {
            statusDados.innerHTML = `
                <div class="alert alert-success mb-0">
                    <i class="fas fa-check-circle"></i> ${data.resultado}
                </div>
                <div class="mt-3">
                    <button id="btnCarregarEstatisticas" class="btn btn-outline-primary">
                        <i class="fas fa-chart-bar"></i> Carregar Estatísticas
                    </button>
                </div>
            `;
            
            document.getElementById('btnCarregarEstatisticas').addEventListener('click', carregarEstatisticas);
        } else {
            statusDados.innerHTML = `
                <div class="alert alert-warning mb-0">
                    <i class="fas fa-exclamation-triangle"></i> Nenhum dado histórico carregado.
                </div>
                <div class="mt-3">
                    <p>Clique em "Baixar Dados Atualizados" para obter os dados históricos da Mega Sena.</p>
                </div>
            `;
        }
    } catch (error) {
        console.error('Erro ao verificar status dos dados:', error);
        mostrarAlerta('Erro ao verificar status dos dados. Verifique o console para mais detalhes.', 'danger');
    }
}

async function carregarDados() {
    try {
        const response = await fetch('/api/dados/carregar');
        const data = await response.json();
        
        if (data.sucesso) {
            mostrarAlerta(data.resultado, 'success');
            verificarStatusDados();
        } else {
            mostrarAlerta(data.resultado, 'warning');
        }
    } catch (error) {
        console.error('Erro ao carregar dados:', error);
        mostrarAlerta('Erro ao carregar dados. Verifique o console para mais detalhes.', 'danger');
    }
}

async function baixarDados() {
    try {
        mostrarAlerta('Baixando dados históricos da Mega Sena...', 'info');
        
        const response = await fetch('/api/dados/baixar');
        const data = await response.json();
        
        if (data.sucesso) {
            mostrarAlerta(data.resultado, 'success');
            verificarStatusDados();
        } else {
            mostrarAlerta(data.resultado, 'warning');
        }
    } catch (error) {
        console.error('Erro ao baixar dados:', error);
        mostrarAlerta('Erro ao baixar dados. Verifique o console para mais detalhes.', 'danger');
    }
}

async function adicionarSorteio(event) {
    event.preventDefault();
    
    const inputNumeros = document.getElementById('inputNumeros').value;
    const numeros = inputNumeros.split(',').map(n => parseInt(n.trim())).filter(n => !isNaN(n));
    
    if (numeros.length !== 6) {
        mostrarAlerta('Você deve informar exatamente 6 números válidos.', 'warning');
        return;
    }
    
    for (const num of numeros) {
        if (num < 1 || num > 60) {
            mostrarAlerta(`O número ${num} está fora do intervalo válido (1-60).`, 'warning');
            return;
        }
    }
    
    try {
        const response = await fetch('/api/sorteios/adicionar', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ numeros })
        });
        
        const data = await response.json();
        
        if (data.sucesso) {
            mostrarAlerta(data.resultado, 'success');
            document.getElementById('inputNumeros').value = '';
            verificarStatusDados();
        } else {
            mostrarAlerta(data.resultado, 'warning');
        }
    } catch (error) {
        console.error('Erro ao adicionar sorteio:', error);
        mostrarAlerta('Erro ao adicionar sorteio. Verifique o console para mais detalhes.', 'danger');
    }
}

async function carregarEstatisticas() {
    try {
        document.getElementById('loadingEstatisticas').style.display = 'block';
        document.getElementById('conteudoEstatisticas').style.display = 'none';
        
        const response = await fetch('/api/estatisticas');
        const data = await response.json();
        
        if (data.sucesso) {
            const estatisticas = data.resultado;
            
            // Exibir números mais frequentes
            const maisFrequentes = document.getElementById('numerosMaisFrequentes');
            maisFrequentes.innerHTML = '';
            for (const [numero, frequencia] of estatisticas.mais_frequentes) {
                maisFrequentes.innerHTML += `
                    <div class="d-flex flex-column align-items-center m-2">
                        <div class="numero-bola">${numero}</div>
                        <small>${frequencia}x</small>
                    </div>
                `;
            }
            
            // Exibir números menos frequentes
            const menosFrequentes = document.getElementById('numerosMenosFrequentes');
            menosFrequentes.innerHTML = '';
            for (const [numero, frequencia] of estatisticas.menos_frequentes) {
                menosFrequentes.innerHTML += `
                    <div class="d-flex flex-column align-items-center m-2">
                        <div class="numero-bola">${numero}</div>
                        <small>${frequencia}x</small>
                    </div>
                `;
            }
            
            // Gráfico de paridade
            const ctxParidade = document.getElementById('graficoParidade').getContext('2d');
            new Chart(ctxParidade, {
                type: 'pie',
                data: {
                    labels: ['Pares', 'Ímpares'],
                    datasets: [{
                        data: [
                            estatisticas.distribuicao_paridade.percentual_pares,
                            estatisticas.distribuicao_paridade.percentual_impares
                        ],
                        backgroundColor: ['#0d6efd', '#6c757d']
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            position: 'bottom'
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    return `${context.label}: ${context.raw.toFixed(2)}%`;
                                }
                            }
                        }
                    }
                }
            });
            
            // Gráfico de dezenas
            const ctxDezenas = document.getElementById('graficoDezenas').getContext('2d');
            new Chart(ctxDezenas, {
                type: 'bar',
                data: {
                    labels: estatisticas.distribuicao_dezenas.dezenas,
                    datasets: [{
                        label: 'Percentual',
                        data: estatisticas.distribuicao_dezenas.percentuais,
                        backgroundColor: '#0d6efd'
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            display: false
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    return `${context.raw.toFixed(2)}%`;
                                }
                            }
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                callback: function(value) {
                                    return value + '%';
                                }
                            }
                        }
                    }
                }
            });
            
            // Exibir gráfico de frequência
            const graficoFrequencia = document.getElementById('graficoFrequencia');
            graficoFrequencia.innerHTML = `<img src="data:image/png;base64,${estatisticas.grafico_frequencia}" class="img-grafico" alt="Frequência dos Números">`;
            
            // Exibir conteúdo
            document.getElementById('loadingEstatisticas').style.display = 'none';
            document.getElementById('conteudoEstatisticas').style.display = 'block';
            
            // Rolar para a seção de estatísticas
            document.getElementById('estatisticas').scrollIntoView({ behavior: 'smooth', block: 'start' });
        } else {
            mostrarAlerta(data.resultado, 'warning');
            document.getElementById('loadingEstatisticas').style.display = 'none';
        }
    } catch (error) {
        console.error('Erro ao carregar estatísticas:', error);
        mostrarAlerta('Erro ao carregar estatísticas. Verifique o console para mais detalhes.', 'danger');
        document.getElementById('loadingEstatisticas').style.display = 'none';
    }
}

async function detectarRaizes(event) {
    event.preventDefault();
    
    const tamanhoJanela = parseInt(document.getElementById('tamanhoJanela').value);
    const numeroRaizes = parseInt(document.getElementById('numeroRaizes').value);
    
    if (isNaN(tamanhoJanela) || tamanhoJanela < 10) {
        mostrarAlerta('O tamanho da janela deve ser pelo menos 10.', 'warning');
        return;
    }
    
    if (isNaN(numeroRaizes) || numeroRaizes < 1 || numeroRaizes > 6) {
        mostrarAlerta('O número de raízes deve estar entre 1 e 6.', 'warning');
        return;
    }
    
    try {
        document.getElementById('loadingRaizes').style.display = 'block';
        document.getElementById('resultadoRaizes').style.display = 'none';
        
        const response = await fetch('/api/raizes/detectar', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ tamanho_janela: tamanhoJanela, n_raizes: numeroRaizes })
        });
        
        const data = await response.json();
        
        if (data.sucesso) {
            const resultado = data.resultado;
            
            // Exibir raízes recentes
            const raizesRecentes = document.getElementById('raizesRecentes');
            raizesRecentes.innerHTML = criarBolasNumeros(resultado.raizes_recentes, 'numero-bola-grande');
            
            // Exibir pontos de mudança
            const pontosMudanca = document.getElementById('pontosMudanca');
            if (resultado.pontos_mudanca.length > 0) {
                let html = '<div class="list-group">';
                for (const ponto of resultado.pontos_mudanca) {
                    html += `
                        <div class="list-group-item">
                            <div class="d-flex w-100 justify-content-between">
                                <h5 class="mb-1">Mudança no sorteio ${ponto.inicio_sorteio}</h5>
                                <small>Diferença: ${(ponto.diferenca * 100).toFixed(0)}%</small>
                            </div>
                            <p class="mb-1">Raízes antes: ${criarBolasNumeros(ponto.raizes_antes, 'numero-bola-pequena')}</p>
                            <p class="mb-0">Raízes depois: ${criarBolasNumeros(ponto.raizes_depois, 'numero-bola-pequena')}</p>
                        </div>
                    `;
                }
                html += '</div>';
                pontosMudanca.innerHTML = html;
            } else {
                pontosMudanca.innerHTML = '<div class="alert alert-info">Nenhum ponto de mudança significativo detectado.</div>';
            }
            
            // Exibir gráfico de evolução
            const graficoEvolucaoRaizes = document.getElementById('graficoEvolucaoRaizes');
            graficoEvolucaoRaizes.innerHTML = `<img src="data:image/png;base64,${resultado.grafico_evolucao}" class="img-grafico" alt="Evolução dos Números Raízes">`;
            
            // Exibir resultado
            document.getElementById('loadingRaizes').style.display = 'none';
            document.getElementById('resultadoRaizes').style.display = 'block';
            
            mostrarAlerta(`Detectados ${resultado.total_janelas} janelas e ${resultado.total_pontos_mudanca} pontos de mudança.`, 'success');
        } else {
            mostrarAlerta(data.resultado, 'warning');
            document.getElementById('loadingRaizes').style.display = 'none';
        }
    } catch (error) {
        console.error('Erro ao detectar números raízes:', error);
        mostrarAlerta('Erro ao detectar números raízes. Verifique o console para mais detalhes.', 'danger');
        document.getElementById('loadingRaizes').style.display = 'none';
    }
}

async function gerarPrevisoes(event) {
    event.preventDefault();
    
    const numeroPrevisoes = parseInt(document.getElementById('numeroPrevisoes').value);
    
    if (isNaN(numeroPrevisoes) || numeroPrevisoes < 1 || numeroPrevisoes > 10) {
        mostrarAlerta('O número de previsões deve estar entre 1 e 10.', 'warning');
        return;
    }
    
    try {
        document.getElementById('loadingPrevisoes').style.display = 'block';
        document.getElementById('resultadoPrevisoes
(Content truncated due to size limit. Use line ranges to read in chunks)