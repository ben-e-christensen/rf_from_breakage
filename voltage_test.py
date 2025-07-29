import time
from daqhats import mcc118, OptionFlags, HatIDs
import sys
sys.path.append('/home/ben/Desktop/repos/daqhats/examples/python/mcc118')
from daqhats_utils import select_hat_device, chan_list_to_mask

class RealTimeDerivative:
    def __init__(self, threshold):
        self.prev_time = None
        self.prev_value = None
        self.threshold = threshold

    def update(self, value):
        current_time = time.time()
        #print(value)

        if self.prev_time is None:
            self.prev_time = current_time
            self.prev_value = value
            return False  # Not enough data yet

        dt = current_time - self.prev_time
        dv = value - self.prev_value
        derivative = dv / dt if dt > 0 else 0
        print(f"Voltage: {value}")
        print(f"dV/dt: {derivative}")

        self.prev_time = current_time
        self.prev_value = value

        return derivative < self.threshold


channels = [2]
channel_mask = chan_list_to_mask(channels)
num_channels = len(channels)
scan_rate = 1000.0
samples_per_channel = 0
options = OptionFlags.CONTINUOUS

address = select_hat_device(HatIDs.MCC_118)
hat = mcc118(address)

hat.a_in_scan_start(channel_mask, samples_per_channel, scan_rate, options)
timeout = 5.0

deriv = RealTimeDerivative(threshold=-.5)  # adjust threshold

READ_ALL_AVAILABLE = -1

acquisition = False

while True:
    read_result = hat.a_in_scan_read(READ_ALL_AVAILABLE, timeout)
    voltage=0
    if read_result.hardware_overrun or read_result.buffer_overrun:
        break

    samples_read_per_channel = int(len(read_result.data) / num_channels)
    if samples_read_per_channel > 0:
        index = samples_read_per_channel * num_channels - num_channels
        voltage = read_result.data[index]

    #voltage = daq.a_in_read(0)  # Read channel 0
    if not acquisition:
        if deriv.update(voltage):
            # send trigger for data acquisition
            deriv.threshold = -30 
            acquisition = True
    
    if acquisition:
        if deriv.update(voltage):
            # send trigger to end data acquisition
            deriv.threshold = -.5
            acquisition = False

    time.sleep(.05)  # sample every 50 ms (adjust if needed)




# def start_voltmeter_loop():
#     channels = [0]
#     channel_mask = chan_list_to_mask(channels)
#     num_channels = len(channels)
#     scan_rate = 1000.0
#     samples_per_channel = 0
#     options = OptionFlags.CONTINUOUS

#     address = select_hat_device(HatIDs.MCC_118)
#     hat = mcc118(address)

#     hat.a_in_scan_start(channel_mask, samples_per_channel, scan_rate, options)
#     timeout = 5.0

#     while True:
#         read_result = hat.a_in_scan_read(READ_ALL_AVAILABLE, timeout)

#         if read_result.hardware_overrun or read_result.buffer_overrun:
#             break

#         samples_read_per_channel = int(len(read_result.data) / num_channels)
#         if samples_read_per_channel > 0:
#             index = samples_read_per_channel * num_channels - num_channels
#             val = read_result.data[index]
#             with state_lock:
#                 shared_state["voltage"] = f"{val:.3f}"
#             update_voltage(f"Voltage: {val:.3f} V")

#         time.sleep(0.2)
