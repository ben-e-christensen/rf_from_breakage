import pyvisa
import matplotlib.pyplot as plt
import time

# Initialize VISA connection
rm = pyvisa.ResourceManager('@py')
scope = rm.open_resource("USB0::1689::1324::B026426::0::INSTR")
scope.timeout = 5000  # 5 second timeout

# Setup acquisition parameters
scope.write("DATA:SOURCE CH1")      # Use channel 1
scope.write("DATA:ENCdg ASCii")     # ASCII encoding
scope.write("DATA:WIDth 1")         # 1 byte per point
scope.write("DATA:START 1")
scope.write("DATA:STOP 1000")       # You can change this if needed

# Clear old data and set to normal acquisition mode
scope.write("ACQ:STOPA SEQ")        # Stop after one acquisition (optional)
scope.write("ACQ:MODE SAMPLE")      # Regular sampling mode
scope.write("ACQ:STATE OFF")        # Ensure it's off before we start
scope.write("ACQ:CLEAR")            # Clear previous data

# Start acquisition
scope.write("ACQ:STATE ON")
time.sleep(5)                       # Collect data for 5 seconds
scope.write("ACQ:STATE OFF")        # Stop acquisition

# Now read waveform data
raw_data = scope.query("CURVe?")
points = [float(p) for p in raw_data.strip().split(',')]

# Scaling parameters
xincr = float(scope.query("WFMPRE:XINCR?"))
xzero = float(scope.query("WFMPRE:XZERO?"))
ymult = float(scope.query("WFMPRE:YMULT?"))
yoff = float(scope.query("WFMPRE:YOFF?"))
yzero = float(scope.query("WFMPRE:YZERO?"))

# Convert to real voltages and time
voltages = [(y - yoff) * ymult + yzero for y in points]
times = [xzero + i * xincr for i in range(len(voltages))]

# Plot
plt.plot(times, voltages)
plt.xlabel("Time (s)")
plt.ylabel("Voltage (V)")
plt.title("Waveform from MDO34 CH1 (5s Acquisition)")
plt.grid()
plt.show()
