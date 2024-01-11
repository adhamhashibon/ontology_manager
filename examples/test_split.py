

txt = "EMMO_eeb8118c_b290_4f57_b0f8_bd65bb6d77ad"
prefix ="EMMO_"

if txt.startswith(prefix):
	x = txt.split(prefix, 2)[-1]
	print(x)
