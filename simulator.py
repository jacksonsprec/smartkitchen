# Simulador Smart Kitchen - exaustão e economia com VFD
# Executar: python "SMART KITCHEN/simulator.py"

import tkinter as tk
from tkinter import ttk
from math import pow
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Modelo simplificado baseado em regras típicas de ventilação de cozinhas industriais.
# Observação: Este script NÃO substitui cálculos normativos; é uma simulação pedagógica.

def required_exhaust_flow(num_appliances: int, base_flow_per_appliance=1.2, safety_factor=1.5, min_flow=2.1):
    """
    Calcula vazão de exaustão requerida (m3/s) como uma aproximação.
    - base_flow_per_appliance: vazão média por equipamento ligado (m3/s)
    - safety_factor: fator de segurança para variações e utilização real
    - min_flow: vazão mínima do sistema (m3/s)
    """
    flow = num_appliances * base_flow_per_appliance * safety_factor
    if flow < min_flow:
        flow = min_flow
    return flow


def fan_power_at_speed_fraction(p_max_kw: float, speed_fraction: float, min_fraction=0.3):
    """
    Potência do ventilador (kW) baseada na lei de afinidade aproximada: P ~ (velocidade)^3
    speed_fraction: fração da vazão máxima (0..1)
    min_fraction: fração mínima do ventilador quando em modo baixo (não 0)
    """
    if speed_fraction < min_fraction:
        speed_fraction = min_fraction
    return p_max_kw * pow(speed_fraction, 3)


def compute_energy_and_savings(num_appliances: int, hours_on_per_day: float, p_max_kw: float,
                               max_flow_m3s: float, base_flow_per_appliance: float=1.2,
                               min_speed_frac: float=0.30):
    """
    Calcula energia consumida com VFD (variando velocidade) vs ventilador a 100% durante 24h.
    Retorna (required_flow, energy_full_kwh, energy_vfd_kwh, savings_kwh, savings_percent)
    """
    required_flow = required_exhaust_flow(num_appliances, base_flow_per_appliance)
    needed_fraction = required_flow / max_flow_m3s
    if needed_fraction > 1.0:
        needed_fraction = 1.0

    # Energia ventilador 100% durante 24h
    energy_full_kwh = p_max_kw * 24.0

    # Energia com VFD: horas em que cozinha está ativa -> potência proporcional ao cubo da velocidade
    p_on_kw = fan_power_at_speed_fraction(p_max_kw, needed_fraction, min_speed_frac)
    energy_on_kwh = p_on_kw * hours_on_per_day

    # Nas horas em que cozinha está inativa, ventilador roda em mínimo
    hours_off = 24.0 - hours_on_per_day
    p_off_kw = fan_power_at_speed_fraction(p_max_kw, min_speed_frac, min_speed_frac)
    energy_off_kwh = p_off_kw * hours_off

    energy_vfd_kwh = energy_on_kwh + energy_off_kwh

    savings_kwh = energy_full_kwh - energy_vfd_kwh
    savings_percent = (savings_kwh / energy_full_kwh) * 100.0 if energy_full_kwh > 0 else 0.0

    return {
        'required_flow': required_flow,
        'needed_fraction': needed_fraction,
        'energy_full_kwh': energy_full_kwh,
        'energy_vfd_kwh': energy_vfd_kwh,
        'savings_kwh': savings_kwh,
        'savings_percent': savings_percent
    }


class SmartKitchenApp:
    CFM_TO_M3S = 0.00047194745
    HP_TO_KW = 0.745699872

    LANG_STRINGS = {
        'Português': {
            'title': 'Simulador Smart Kitchen - Exaustão e VFD',
            'language_label': 'Idioma:',
            'num_label': 'Número de equipamentos ligados:',
            'hours_label': 'Horas por dia com equipamentos ligados:',
            'pmax_label': 'Potência máxima do ventilador (kW):',
            'max_flow_label': 'Vazão máxima do sistema (m³/s):',
            'base_flow_label': 'Vazão por equipamento (m³/s):',
            'min_frac_label': 'Fração mínima do ventilador (modo baixo):',
            'calc_btn': 'Calcular',
            'required_flow': 'Vazão requerida',
            'fraction': 'Fração da vazão máxima exigida',
            'energy_full': 'Energia - ventilador 100% (24h)',
            'energy_vfd': 'Energia - com VFD',
            'savings': 'Economia estimada',
            'graph1_title': 'Vazão requerida (m³/s)',
            'graph1_xlabel': 'Equipamentos ligados',
            'graph1_ylabel': 'm³/s',
            'graph2_title': 'Consumo energético',
            'graph2_ylabel': 'kWh/dia',
            'bar1': '100% 24h',
            'bar2': 'VFD (estim)'
        },
        'English': {
            'title': 'Smart Kitchen Simulator - Exhaust and VFD',
            'language_label': 'Language:',
            'num_label': 'Number of appliances on:',
            'hours_label': 'Hours per day appliances on:',
            'pmax_label': 'Fan maximum power (hp):',
            'max_flow_label': 'System maximum flow (CFM):',
            'base_flow_label': 'Flow per appliance (CFM):',
            'min_frac_label': 'Minimum fan fraction (low mode):',
            'calc_btn': 'Calculate',
            'required_flow': 'Required flow',
            'fraction': 'Required flow fraction',
            'energy_full': 'Energy - fan 100% (24h)',
            'energy_vfd': 'Energy - with VFD',
            'savings': 'Estimated savings',
            'graph1_title': 'Required flow (CFM)',
            'graph1_xlabel': 'Appliances on',
            'graph1_ylabel': 'CFM',
            'graph2_title': 'Energy consumption',
            'graph2_ylabel': 'kWh/day',
            'bar1': '100% 24h',
            'bar2': 'VFD (est)'
        }
    }

    def __init__(self, root):
        self.root = root
        self.language_var = tk.StringVar(value='Português')
        self.last_language = 'Português'
        root.title(self.get_text('title'))

        frm = ttk.Frame(root, padding=12)
        frm.grid(row=0, column=0, sticky='NSEW')

        # Entradas
        self.num_label = ttk.Label(frm, text=self.get_text('num_label'))
        self.num_label.grid(row=0, column=0, sticky='W')
        self.num_appliances_var = tk.IntVar(value=3)
        self.num_spin = ttk.Spinbox(frm, from_=0, to=50, textvariable=self.num_appliances_var, width=6, command=self.update_all)
        self.num_spin.grid(row=0, column=1, sticky='W')

        self.hours_label = ttk.Label(frm, text=self.get_text('hours_label'))
        self.hours_label.grid(row=1, column=0, sticky='W')
        self.hours_var = tk.DoubleVar(value=8.0)
        self.hours_spin = ttk.Spinbox(frm, from_=0, to=24, increment=0.5, textvariable=self.hours_var, width=6, command=self.update_all)
        self.hours_spin.grid(row=1, column=1, sticky='W')

        self.pmax_label = ttk.Label(frm, text=self.get_text('pmax_label'))
        self.pmax_label.grid(row=2, column=0, sticky='W')
        self.pmax_var = tk.DoubleVar(value=5.0)
        self.pmax_entry = ttk.Entry(frm, textvariable=self.pmax_var, width=8)
        self.pmax_entry.grid(row=2, column=1, sticky='W')

        self.max_flow_label = ttk.Label(frm, text=self.get_text('max_flow_label'))
        self.max_flow_label.grid(row=3, column=0, sticky='W')
        self.max_flow_var = tk.DoubleVar(value=20.0)
        self.max_flow_entry = ttk.Entry(frm, textvariable=self.max_flow_var, width=8)
        self.max_flow_entry.grid(row=3, column=1, sticky='W')

        self.base_flow_label = ttk.Label(frm, text=self.get_text('base_flow_label'))
        self.base_flow_label.grid(row=4, column=0, sticky='W')
        self.base_flow_var = tk.DoubleVar(value=1.2)
        self.base_flow_entry = ttk.Entry(frm, textvariable=self.base_flow_var, width=8)
        self.base_flow_entry.grid(row=4, column=1, sticky='W')

        self.min_frac_label = ttk.Label(frm, text=self.get_text('min_frac_label'))
        self.min_frac_label.grid(row=5, column=0, sticky='W')
        self.min_frac_var = tk.DoubleVar(value=0.30)
        self.min_frac_spin = ttk.Spinbox(frm, from_=0.05, to=0.8, increment=0.05, textvariable=self.min_frac_var, width=6, command=self.update_all)
        self.min_frac_spin.grid(row=5, column=1, sticky='W')

        self.lang_label = ttk.Label(frm, text=self.get_text('language_label'))
        self.lang_label.grid(row=6, column=0, sticky='W')
        self.lang_combo = ttk.Combobox(frm, values=list(self.LANG_STRINGS.keys()), state='readonly', textvariable=self.language_var, width=10)
        self.lang_combo.grid(row=6, column=1, sticky='W')
        self.lang_combo.bind('<<ComboboxSelected>>', lambda e: self.update_language())

        # Botões
        self.calc_btn = ttk.Button(frm, text=self.get_text('calc_btn'), command=self.update_all)
        self.calc_btn.grid(row=7, column=0, columnspan=2, pady=(8,8))

        # Resultados texto
        self.result_text = tk.Text(frm, width=50, height=6)
        self.result_text.grid(row=8, column=0, columnspan=2, pady=(4,4))

        # Gráficos (matplotlib embutido)
        # aumentar altura do gráfico em ~10% para evitar corte de legendas
        # altura anterior: 3.3 -> aumento 10% = 3.63
        self.fig, (self.ax1, self.ax2) = plt.subplots(1,2, figsize=(8,3.63))
        plt.tight_layout()
        self.canvas = FigureCanvasTkAgg(self.fig, master=frm)
        self.canvas.get_tk_widget().grid(row=0, column=2, rowspan=9, padx=(12,0))

        self.update_all()

    def get_text(self, key):
        return self.LANG_STRINGS[self.language_var.get()][key]

    def display_to_internal(self, pmax, max_flow, base_flow, language):
        if language == 'English':
            return (
                pmax * self.HP_TO_KW,
                max_flow * self.CFM_TO_M3S,
                base_flow * self.CFM_TO_M3S
            )
        return pmax, max_flow, base_flow

    def internal_to_display(self, pmax_kw, max_flow_m3s, base_flow_m3s, language):
        if language == 'English':
            return (
                pmax_kw / self.HP_TO_KW,
                max_flow_m3s / self.CFM_TO_M3S,
                base_flow_m3s / self.CFM_TO_M3S
            )
        return pmax_kw, max_flow_m3s, base_flow_m3s

    def update_language(self):
        new_lang = self.language_var.get()
        if new_lang != self.last_language:
            try:
                pmax = float(self.pmax_var.get())
                max_flow = float(self.max_flow_var.get())
                base_flow = float(self.base_flow_var.get())
            except Exception:
                pmax, max_flow, base_flow = 5.0, 20.0, 1.2

            internal_values = self.display_to_internal(pmax, max_flow, base_flow, self.last_language)
            pmax_disp, max_flow_disp, base_flow_disp = self.internal_to_display(
                internal_values[0], internal_values[1], internal_values[2], new_lang
            )
            self.pmax_var.set(round(pmax_disp, 3))
            self.max_flow_var.set(round(max_flow_disp, 3))
            self.base_flow_var.set(round(base_flow_disp, 3))

            self.last_language = new_lang

        root_title = self.get_text('title')
        self.root.title(root_title)
        self.num_label.config(text=self.get_text('num_label'))
        self.hours_label.config(text=self.get_text('hours_label'))
        self.pmax_label.config(text=self.get_text('pmax_label'))
        self.max_flow_label.config(text=self.get_text('max_flow_label'))
        self.base_flow_label.config(text=self.get_text('base_flow_label'))
        self.min_frac_label.config(text=self.get_text('min_frac_label'))
        self.lang_label.config(text=self.get_text('language_label'))
        self.calc_btn.config(text=self.get_text('calc_btn'))
        self.update_all()

    def update_all(self):
        language = self.language_var.get()
        try:
            num = int(self.num_appliances_var.get())
            hours = float(self.hours_var.get())
            pmax = float(self.pmax_var.get())
            maxflow = float(self.max_flow_var.get())
            base_flow = float(self.base_flow_var.get())
            min_frac = float(self.min_frac_var.get())
        except Exception:
            return

        pmax_kw, maxflow_m3s, base_flow_m3s = self.display_to_internal(pmax, maxflow, base_flow, language)
        res = compute_energy_and_savings(num, hours, pmax_kw, maxflow_m3s, base_flow_m3s, min_frac)

        if language == 'English':
            required_flow = res['required_flow'] / self.CFM_TO_M3S
            flow_unit = 'CFM'
        else:
            required_flow = res['required_flow']
            flow_unit = 'm³/s'

        self.result_text.delete('1.0', tk.END)
        self.result_text.insert(tk.END, f"{self.get_text('required_flow')}: {required_flow:.2f} {flow_unit}\n")
        self.result_text.insert(tk.END, f"{self.get_text('fraction')}: {res['needed_fraction']*100:.1f}%\n")
        self.result_text.insert(tk.END, f"{self.get_text('energy_full')}: {res['energy_full_kwh']:.2f} kWh/day\n" if language == 'English' else f"{self.get_text('energy_full')}: {res['energy_full_kwh']:.2f} kWh/dia\n")
        self.result_text.insert(tk.END, f"{self.get_text('energy_vfd')}: {res['energy_vfd_kwh']:.2f} kWh/day\n" if language == 'English' else f"{self.get_text('energy_vfd')}: {res['energy_vfd_kwh']:.2f} kWh/dia\n")
        self.result_text.insert(tk.END, f"{self.get_text('savings')}: {res['savings_kwh']:.2f} kWh/day ({res['savings_percent']:.1f}%)\n" if language == 'English' else f"{self.get_text('savings')}: {res['savings_kwh']:.2f} kWh/dia ({res['savings_percent']:.1f}%)\n")

        self.ax1.clear()
        self.ax2.clear()

        xs = list(range(0, max(6, num+3)))
        ys_internal = [required_exhaust_flow(x, base_flow_m3s) for x in xs]
        if language == 'English':
            ys = [y / self.CFM_TO_M3S for y in ys_internal]
        else:
            ys = ys_internal

        self.ax1.plot(xs, ys, marker='o')
        self.ax1.set_title(self.get_text('graph1_title'))
        self.ax1.set_xlabel(self.get_text('graph1_xlabel'))
        self.ax1.set_ylabel(self.get_text('graph1_ylabel'))
        self.ax1.axvline(num, color='red', linestyle='--')

        bars = [self.get_text('bar1'), self.get_text('bar2')]
        vals = [res['energy_full_kwh'], res['energy_vfd_kwh']]
        colors = ['gray', 'green']
        self.ax2.bar(bars, vals, color=colors)
        self.ax2.set_ylabel(self.get_text('graph2_ylabel'))
        self.ax2.set_title(self.get_text('graph2_title'))

        self.fig.tight_layout(pad=1.0)
        self.fig.subplots_adjust(bottom=0.18, top=0.92, left=0.12, right=0.98, wspace=0.35)

        self.canvas.draw()


if __name__ == '__main__':
    root = tk.Tk()
    app = SmartKitchenApp(root)
    # aumentar a altura da janela em ~10% após o layout ser calculado
    root.update_idletasks()
    try:
        w = root.winfo_width() or root.winfo_reqwidth()
        h = root.winfo_height() or root.winfo_reqheight()
        new_h = int(h * 1.1)
        root.geometry(f"{w}x{new_h}")
    except Exception:
        pass
    root.mainloop()
