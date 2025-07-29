import pyvisa
import matplotlib.pyplot as plt

rm = pyvisa.ResourceManager('@py')
scope = rm.open_resource("USB0::1689::1324::B026426::0::INSTR")
scope.timeout = 5000

scope.write("DATA:SOURCE CH1")
scope.write("DATA:ENCdg ASCii")
scope.write("DATA:WIDth 1")
scope.write("DATA:START 1")
scope.write("DATA:STOP 100000")


data = scope.query("CURVe?")
points = [float(p) for p in data.strip().split(',')]

# Get scaling
xincr = float(scope.query("WFMPRE:XINCR?"))
xzero = float(scope.query("WFMPRE:XZERO?"))
ymult = float(scope.query("WFMPRE:YMULT?"))
yoff = float(scope.query("WFMPRE:YOFF?"))
yzero = float(scope.query("WFMPRE:YZERO?"))

print(f"xincr val: {xincr}")
print(f"xzero val: {xzero}")
print(f"ymult val: {ymult}")
print(f"yoff val: {yoff}")
print(f"yzero val: {yzero}")

voltages = [(y - yoff) * ymult + yzero for y in points]
times = [xzero + i * xincr for i in range(len(voltages))]

plt.plot(times, voltages)
plt.xlabel("Time (s)")
plt.ylabel("Voltage (V)")
plt.title("Waveform from MDO34 CH1")
plt.grid()
plt.show()
