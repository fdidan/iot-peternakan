def evaluate_rules(data):
    """
    Evaluasi data sensor dan return list of actions
    """
    actions = []

    # Rule 1: Amonia tinggi -> buka jendela
    if data.get("ammonia", 0) > 25:
        actions.append("OPEN_WINDOW")
    else:
        # Jika amonia rendah, tutup jendela
        if data.get("ammonia", 0) < 10:
            actions.append("CLOSE_WINDOW")

    # Rule 2: Suhu tinggi + kelembaban tinggi -> nyalakan kipas
    if data.get("temperature", 0) > 30 and data.get("humidity", 0) > 70:
        actions.append("FAN_ON")
    # Jika kondisi normal, matikan kipas
    elif data.get("temperature", 0) < 28 and data.get("humidity", 0) < 60:
        actions.append("FAN_OFF")

    # Rule 3: Suhu rendah -> nyalakan pemanas
    if data.get("temperature", 0) < 22:
        actions.append("HEATER_ON")
    # Jika suhu sudah cukup, matikan pemanas
    elif data.get("temperature", 0) > 25:
        actions.append("HEATER_OFF")

    return actions
