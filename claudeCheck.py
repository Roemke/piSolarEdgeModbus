import solaredge_modbus

inv = solaredge_modbus.Inverter(host='192.168.0.205', port=1502, timeout=5)
inv.connect()

v = inv.read_all()
meter = inv.meters()['Meter1'].read_all()
bat = inv.batteries()['Battery1'].read_all()

inv.disconnect()

ac_out   = v['power_ac']   * (10 ** v['power_ac_scale'])
grid     = meter['power']  * (10 ** meter['power_scale'])
bat_power = bat['instantaneous_power']  # positiv=laden, negativ=entladen

print(f"AC out:    {ac_out:>8.0f} W")
print(f"Grid:      {grid:>8.0f} W  (+ = export, - = import)")
print(f"Bat power: {bat_power:>8.0f} W  (+ = laden, - = entladen)")