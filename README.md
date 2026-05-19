Simulador Smart Kitchen

Descrição
- Aplicação GUI em Python que simula a vazão de exaustão necessária para uma coifa comercial
  e estima economia de energia ao usar um VFD (inversor de frequência) comparado ao uso
  do ventilador em 100% o dia inteiro.

Descrição detalhada
- Português: Este simulador em `SMART KITCHEN/simulator.py` é uma ferramenta gráfica para estimar exaustão e economia de energia em uma cozinha industrial com ventilador de velocidade variável (VFD). Ele usa `tkinter` para a interface e `matplotlib` para gerar gráficos.
  - calcula a vazão de exaustão necessária com base no número de equipamentos ligados
  - estima a potência do ventilador usando uma relação cúbica entre velocidade e consumo
  - compara consumo energético de um ventilador operando a 100% durante 24h com um ventilador controlado por VFD
  - mostra economia em kWh/dia e porcentagem
  - exibe gráficos de vazão requerida e consumo energético
  - suporta idioma em Português e Inglês, com conversão de unidades entre m³/s e CFM / kW e HP
  - observação: é um modelo simplificado de caráter pedagógico e não substitui cálculos normativos.

- English:
This simulator in `SMART KITCHEN/simulator.py` is a GUI tool to estimate exhaust requirements and energy savings for an industrial kitchen using a variable frequency drive (VFD) fan. It uses `tkinter` for the user interface and `matplotlib` for charting.
  - computes required exhaust flow based on the number of appliances turned on
  - estimates fan power using an approximate cubic speed-power relationship
  - compares energy use of a fan running at 100% for 24h versus a VFD-controlled fan
  - displays estimated savings in kWh/day and percentage
  - includes graphs for required flow and energy consumption
  - supports Portuguese and English with unit conversion between m³/s and CFM / kW and HP
  - note: this is a simplified educational model and not a replacement for normative engineering calculations.

Como executar
1. Crie e ative um ambiente virtual (recomendado):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r "SMART KITCHEN\requirements.txt"
```

2. Execute o simulador:

```powershell
python "SMART KITCHEN\simulator.py"
```

Notas
- Este é um modelo pedagógico simplificado. Parâmetros como `base_flow_per_appliance`, `safety_factor`
  e `min_speed_frac` podem ser ajustados na interface para aproximar regras como ASHRAE 154 / NBR 14518,
  mas o usuário deve consultar as normas e um engenheiro para projetos reais.

Arquivos
- simulator.py: script principal (GUI)
- requirements.txt: dependências (matplotlib)
