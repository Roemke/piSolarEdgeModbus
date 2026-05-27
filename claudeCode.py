#!/Data/Infos/raspberry/raspiFHEM/solaredge_modbus/venv/bin/python
import solaredge_modbus

inv = solaredge_modbus.Inverter(host='192.168.0.205', port=1502, timeout=5)
inv.connect()

v = inv.read_all()
meter = inv.meters()['Meter1'].read_all()
bat = inv.batteries()['Battery1'].read_all()

inv.disconnect()

# --- Solar (DC vom Panel) ---
solar_in = v['power_dc'] * (10 ** v['power_dc_scale'])

# --- Netz: positiv = Export (ins Netz), negativ = Import (aus Netz) ---
grid_power = meter['power'] * (10 ** meter['power_scale'])
grid_export = max(0, grid_power)   # ins Netz
grid_import = max(0, -grid_power)  # aus Netz

# --- Akku ---
bat_power = bat['instantaneous_power']          # positiv = laden, negativ = entladen
bat_charging   = max(0, bat_power)              # Akku lädt
bat_discharging = max(0, -bat_power)            # Akku entlädt ins Haus

# Verluste beim Entladen (Wirkungsgrad ~93%)
BATTERY_EFFICIENCY = 0.93
bat_to_house = bat_discharging * BATTERY_EFFICIENCY  # was wirklich ankommt
bat_losses   = bat_discharging - bat_to_house

# --- AC vom Inverter ---
ac_out = v['power_ac'] * (10 ** v['power_ac_scale'])

# --- Hausverbrauch ---
# Haus = AC-Ausgang + Akku-Einspeisung + Netzbezug - Netzexport
house = ac_out + bat_to_house + grid_import - grid_export

# --- Ausgabe ---
print(f"☀️  Solar eingehend (DC):       {solar_in:>8.0f} W")
print(f"⚡  Inverter AC-Ausgang:        {ac_out:>8.0f} W")
print(f"")
print(f"🔋  Akku Ladezustand (SOE):     {bat['soe']:>7.1f} %")
if bat_charging > 0:
    print(f"🔋  Akku lädt:                  {bat_charging:>8.0f} W")
elif bat_discharging > 0:
    print(f"🔋  Akku entlädt:               {bat_discharging:>8.0f} W")
    print(f"🔋  → davon im Haus an:         {bat_to_house:>8.0f} W")
    print(f"🔋  → Verluste (~7%):           {bat_losses:>8.0f} W")
else:
    print(f"🔋  Akku: Standby")
print(f"")
if grid_export > 0:
    print(f"🔌  Netz-Export (eingespeist):  {grid_export:>8.0f} W")
else:
    print(f"🔌  Netzbezug:                  {grid_import:>8.0f} W")
print(f"")
print(f"🏠  Hausverbrauch (gesamt):     {house:>8.0f} W")
