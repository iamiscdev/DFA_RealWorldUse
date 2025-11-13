"""
Smart Home Security System Controller using DFA

Real-world application:
- Models security system states (Disarmed, Armed, Triggered, etc.)
- Processes sensor inputs (motion, door, keypad)
- Provides visual simulation of security system behavior
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional
import sys

from automata_dfa import DFA


class SecuritySystemDFAApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Smart Home Security System Controller')
        self.geometry('1000x600')

        self.state_colors = {
            'Disarmed': 'green',
            'Armed_Home': 'yellow',
            'Armed_Away': 'orange',
            'Triggered': 'red',
            'Alarm': 'red',
            'Entry_Delay': 'purple'
        }

        self.dfa: Optional[DFA] = None
        self.security_log = []

        self._create_widgets()
        self.load_security_example()

    def _create_widgets(self):
        main_frame = ttk.Frame(self)
        main_frame.pack(fill='both', expand=True, padx=8, pady=6)

        # Left panel
        left_panel = ttk.LabelFrame(main_frame, text='Security System Status')
        left_panel.pack(side='left', fill='both', expand=True, padx=(0, 8))

        self.status_frame = ttk.Frame(left_panel)
        self.status_frame.pack(fill='x', pady=10)

        ttk.Label(self.status_frame, text='SYSTEM STATUS:', font=('Arial', 14, 'bold')).pack()
        self.status_label = ttk.Label(self.status_frame, text='DISARMED',
                                      font=('Arial', 18, 'bold'), foreground='green')
        self.status_label.pack(pady=5)

        self.state_canvas = tk.Canvas(left_panel, width=200, height=200, bg='white', relief='sunken')
        self.state_canvas.pack(pady=10)
        self.state_indicator = self.state_canvas.create_oval(50, 50, 150, 150, fill='green')

        # Sensor inputs
        sensor_frame = ttk.LabelFrame(left_panel, text='Sensor Inputs')
        sensor_frame.pack(fill='x', pady=10)

        btn_frame = ttk.Frame(sensor_frame)
        btn_frame.pack(fill='x', pady=5)
        ttk.Button(btn_frame, text='ARM HOME', command=lambda: self.add_security_input('arm_home')).pack(side='left', padx=2)
        ttk.Button(btn_frame, text='ARM AWAY', command=lambda: self.add_security_input('arm_away')).pack(side='left', padx=2)
        ttk.Button(btn_frame, text='DISARM', command=lambda: self.add_security_input('disarm')).pack(side='left', padx=2)

        sensor_btn_frame = ttk.Frame(sensor_frame)
        sensor_btn_frame.pack(fill='x', pady=5)
        ttk.Button(sensor_btn_frame, text='MOTION DETECTED', command=lambda: self.add_security_input('motion')).pack(side='left', padx=2)
        ttk.Button(sensor_btn_frame, text='DOOR OPENED', command=lambda: self.add_security_input('door')).pack(side='left', padx=2)
        ttk.Button(sensor_btn_frame, text='WINDOW BREAK', command=lambda: self.add_security_input('window')).pack(side='left', padx=2)

        ttk.Label(sensor_frame, text='Manual Input:').pack(anchor='w', pady=(10, 0))
        input_frame = ttk.Frame(sensor_frame)
        input_frame.pack(fill='x')
        self.manual_entry = ttk.Entry(input_frame)
        self.manual_entry.pack(side='left', fill='x', expand=True)
        ttk.Button(input_frame, text='Send', command=self.send_manual_input).pack(side='right', padx=5)

        ttk.Label(left_panel, text='Security Log:').pack(anchor='w', pady=(10, 0))
        self.log_text = tk.Text(left_panel, height=8, width=50)
        self.log_text.pack(fill='both', expand=True)

        # Right panel
        right_panel = ttk.LabelFrame(main_frame, text='DFA Configuration')
        right_panel.pack(side='right', fill='both', expand=True)

        spec_frame = ttk.Frame(right_panel)
        spec_frame.pack(fill='x', pady=5)
        ttk.Button(spec_frame, text='Load Security Example', command=self.load_security_example).pack(side='left')
        ttk.Button(spec_frame, text='Build Custom DFA', command=self.build_dfa).pack(side='left', padx=5)

        sim_frame = ttk.LabelFrame(right_panel, text='Simulation Control')
        sim_frame.pack(fill='x', pady=10)

        control_frame = ttk.Frame(sim_frame)
        control_frame.pack(fill='x', pady=5)
        ttk.Button(control_frame, text='Reset System', command=self.reset_sim).pack(side='left')
        ttk.Button(control_frame, text='Step', command=self.step_sim).pack(side='left', padx=5)
        ttk.Button(control_frame, text='Run All', command=self.run_sim).pack(side='left', padx=5)

        status_info = ttk.Frame(sim_frame)
        status_info.pack(fill='x', pady=5)
        ttk.Label(status_info, text='Current State:').grid(row=0, column=0, sticky='w')
        self.current_label = ttk.Label(status_info, text='Disarmed', font=('Arial', 10, 'bold'))
        self.current_label.grid(row=0, column=1, sticky='w', padx=5)
        ttk.Label(status_info, text='System Armed:').grid(row=1, column=0, sticky='w')
        self.accept_label = ttk.Label(status_info, text='No')
        self.accept_label.grid(row=1, column=1, sticky='w', padx=5)
        ttk.Label(status_info, text='Input Position:').grid(row=2, column=0, sticky='w')
        self.position_label = ttk.Label(status_info, text='0')
        self.position_label.grid(row=2, column=1, sticky='w', padx=5)

        ttk.Label(right_panel, text='Security State Transitions:').pack(anchor='w', pady=(10, 0))
        self.delta_text = tk.Text(right_panel, height=12)
        self.delta_text.pack(fill='both', expand=True)

    def build_dfa(self):
        messagebox.showinfo("Info", "Custom DFA builder not yet implemented.")
    
    def add_security_input(self, input_type):
        current = self.manual_entry.get()
        if current:
            current += ' ' + input_type
        else:
            current = input_type
        self.manual_entry.delete(0, 'end')
        self.manual_entry.insert(0, current)

    def _normalize_input(self, input_str):
        replacements = {
            'arm home': 'arm_home',
            'arm away': 'arm_away',
            'motion detected': 'motion',
            'door opened': 'door',
            'window broken': 'window',
            'window break': 'window',
            'dis arm': 'disarm',
            'dis_arm': 'disarm',
            'motion sensor': 'motion',
            'door sensor': 'door',
            'delay end': 'delay_end',
            'delay_end': 'delay_end',
            'triggered': 'motion',
            'alarm': 'motion',
            'siren': 'motion'
        }
        normalized = input_str.lower().strip()
        for old, new in replacements.items():
            normalized = normalized.replace(old, new)
        return ' '.join(normalized.split())

    def send_manual_input(self):
        if not self._check_dfa():
            return
        input_str = self.manual_entry.get().strip()
        if input_str:
            normalized_input = self._normalize_input(input_str)
            commands = normalized_input.split()
            valid = ['arm_home', 'arm_away', 'disarm', 'motion', 'door', 'window', 'delay_end']
            invalid = [c for c in commands if c not in valid]
            if invalid:
                messagebox.showwarning('Invalid Commands',
                    f'Ignored unrecognized commands: {", ".join(invalid)}\n'
                    f'Valid: {", ".join(valid)}')
            final_input = ' '.join([c for c in commands if c in valid])
            if final_input:
                self.manual_entry.delete(0, 'end')
                self.manual_entry.insert(0, final_input)
                self.run_sim()
                self.log_security_event(f"Manual input: {final_input}")
            else:
                messagebox.showwarning('No Valid Commands', 'No valid commands found.')

    def load_security_example(self):
        try:
            states = ['Disarmed', 'Armed_Home', 'Armed_Away', 'Entry_Delay', 'Alarm', 'Triggered']
            alphabet = ['arm_home', 'arm_away', 'disarm', 'motion', 'door', 'window', 'delay_end']
            start = 'Disarmed'
            accept = ['Armed_Home', 'Armed_Away']
            transitions = [
                'Disarmed arm_home Armed_Home',
                'Disarmed arm_away Armed_Away',
                'Armed_Home disarm Disarmed',
                'Armed_Away disarm Disarmed',
                'Armed_Home motion Triggered',
                'Armed_Away motion Triggered',
                'Armed_Home door Entry_Delay',
                'Armed_Away door Entry_Delay',
                'Armed_Home window Triggered',
                'Armed_Away window Triggered',
                'Entry_Delay delay_end Alarm',
                'Entry_Delay disarm Disarmed',
                'Alarm disarm Disarmed',
                'Triggered disarm Disarmed',
                'Disarmed motion Disarmed',
                'Disarmed door Disarmed',
                'Disarmed window Disarmed',
                'Disarmed disarm Disarmed',
                'Armed_Home arm_home Armed_Home',
                'Armed_Away arm_away Armed_Away'
            ]

            delta = {}
            for t in transitions:
                src, sym, tgt = t.split()
                delta.setdefault(src, {})[sym] = tgt

            self.dfa = DFA(states=states, alphabet=alphabet, delta=delta, start=start, accept=accept)
            self.update_display()
            self.log_security_event("Security system DFA loaded")
            messagebox.showinfo('Success', 'Security System DFA loaded successfully!')
        except Exception as e:
            messagebox.showerror('Error', f'Failed to load security DFA: {e}')

    def log_security_event(self, event):
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {event}\n"
        self.security_log.append(log_entry)
        self.log_text.delete('1.0', 'end')
        self.log_text.insert('1.0', ''.join(self.security_log[-20:]))
        self.log_text.see('end')

    def _input_str(self) -> str:
        return self.manual_entry.get().strip()

    def reset_sim(self):
        if not self._check_dfa():
            return
        self.dfa.reset()
        self.position_label.config(text='0')
        self.update_display()
        self.log_security_event("System reset to initial state")

    def step_sim(self):
        if not self._check_dfa():
            return
        w = self._normalize_input(self._input_str())
        symbols = w.split()
        pos = int(self.position_label['text'])
        if pos >= len(symbols):
            messagebox.showinfo('End', 'Security sequence complete')
            return
        sym = symbols[pos]
        nxt = self.dfa.step(sym)
        if nxt is None:
            current_state = self.dfa.current
            available = list(self.dfa.delta.get(current_state, {}).keys())
            messagebox.showerror('Error',
                f'Security command "{sym}" not recognized in state "{current_state}".\n'
                f'Available: {", ".join(available)}')
            return
        pos += 1
        self.position_label.config(text=str(pos))
        self.update_display()
        self.log_security_event(f"Processed: {sym} -> State: {nxt}")

    def run_sim(self):
        if not self._check_dfa():
            return
        w = self._normalize_input(self._input_str())
        if not w.strip():
            messagebox.showwarning('No Input', 'Please enter security commands to process.')
            return
        symbols = w.split()
        valid = ['arm_home', 'arm_away', 'disarm', 'motion', 'door', 'window', 'delay_end']
        for sym in symbols:
            if sym not in valid:
                messagebox.showerror('Error', f'Unrecognized command: "{sym}"')
                return
        print("DEBUG: running DFA.accepts on:", symbols)
        res = self.dfa.accepts(symbols)
        if res is None:
            messagebox.showerror('Error', 'Input contains unrecognized security commands')
            return
        self.position_label.config(text=str(len(symbols)))
        self.update_display()
        status_msg = "SECURE" if res else "ALERT - System not properly armed"
        messagebox.showinfo('Security Status', f'Security System Status: {status_msg}')
        self.log_security_event(f"Sequence completed - System secure: {res}")

    def update_display(self):
        if self.dfa is None:
            self.current_label.config(text='-')
            self.accept_label.config(text='-')
            self.status_label.config(text='SYSTEM OFFLINE', foreground='gray')
            self.state_canvas.itemconfig(self.state_indicator, fill='gray')
            return
        current_state = self.dfa.current or 'Disarmed'
        self.current_label.config(text=current_state)
        color = self.state_colors.get(current_state, 'blue')
        self.status_label.config(text=current_state.upper().replace('_', ' '), foreground=color)
        self.state_canvas.itemconfig(self.state_indicator, fill=color)

        w = self._normalize_input(self._input_str())
        pos = int(self.position_label['text'])
        symbols = w.split()[:pos] if w else []
        accepted = self.dfa.accepts(symbols)
        self.accept_label.config(text='ERROR' if accepted is None else ('YES' if accepted else 'NO'))

        lines = ["State       --Command    --> Next State", "-" * 40]
        for s in sorted(self.dfa.delta.keys()):
            for a in sorted(self.dfa.alphabet):
                t = self.dfa.delta.get(s, {}).get(a, '')
                if t:
                    lines.append(f"{s:12} --{a:10}--> {t:12}")
        self.delta_text.delete('1.0', 'end')
        self.delta_text.insert('1.0', '\n'.join(lines))

    def _check_dfa(self) -> bool:
        if self.dfa is None:
            messagebox.showwarning('No DFA', 'Please load security system DFA first')
            return False
        return True


def main():
    app = SecuritySystemDFAApp()
    app.mainloop()


if __name__ == '__main__':
    main()
