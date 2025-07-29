import pyvisa
import time
import matplotlib.pyplot as plt

rm = pyvisa.ResourceManager('@py')
scope = rm.open_resource("USB0::1689::1324::B026426::0::INSTR")
scope.timeout = 10000  # 10 second timeout

# Setup data format
#scope.write("ACQ:STOPA SEQ")
scope.write("DATA:SOURCE CH1")
scope.write("DATA:ENCdg ASCii")   # or RIBinary for speed
scope.write("DATA:WIDth 1")
scope.write("DATA:START 1")
scope.write("DATA:STOP 10000")

# Optional: set to single sequence mode if you want to control when it stops
# scope.write("ACQ:STOPA SEQ")

# Start acquisition
# scope.write("ACQ:STATE RUN")
scope.write("ACQ:STATE ON")         # Start acquisition
print("Acquisition started...")
time.sleep(25)  # Wait 5 seconds (or however long you want)

# Stop acquisition
scope.write("ACQ:STATE STOP")
print("Acquisition stopped.")

# Read waveform
data = scope.query("CURVe?")
points = [float(p) for p in data.strip().split(',')]

# Scaling
xincr = float(scope.query("WFMPRE:XINCR?"))
xzero = float(scope.query("WFMPRE:XZERO?"))
ymult = float(scope.query("WFMPRE:YMULT?"))
yoff = float(scope.query("WFMPRE:YOFF?"))
yzero = float(scope.query("WFMPRE:YZERO?"))

voltages = [(y - yoff) * ymult + yzero for y in points]
times = [xzero + i * xincr for i in range(len(voltages))]

print("First 10 scaled voltages (in V):", voltages[:10])
print("Min V:", min(voltages), "Max V:", max(voltages))
print(times[:10])

# Plot
plt.plot(times, voltages)
plt.xlabel("Time (s)")
plt.ylabel("Voltage (V)")
plt.title("Captured Waveform")
plt.grid()
plt.show()
