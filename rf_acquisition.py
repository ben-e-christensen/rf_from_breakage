import threading
import time
from daqhats import mcc118, OptionFlags, HatIDs
import sys
sys.path.append('/home/ben/Desktop/repos/daqhats/examples/python/mcc118')
from daqhats_utils import select_hat_device, chan_list_to_mask
import subprocess

class RealTimeDerivative:
    def __init__(self, threshold):
        self.prev_time = None
        self.prev_value = None
        self.threshold = threshold

    def update(self, value):
        current_time = time.time()

        if self.prev_time is None:
            self.prev_time = current_time
            self.prev_value = value
            return False

        dt = current_time - self.prev_time
        dv = value - self.prev_value
        derivative = dv / dt if dt > 0 else 0
        print(f"Voltage: {value}")
        print(f"dV/dt: {derivative}")

        self.prev_time = current_time
        self.prev_value = value

        return derivative < self.threshold

def trigger_scope_start():
    print("Triggering scope: START acquisition")
    subprocess.run(["echo", ":ACQ:STATE ON"], stdout=subprocess.PIPE)  # Replace with actual pyvisa command

def trigger_scope_stop():
    print("Triggering scope: STOP + read data")
    subprocess.run(["echo", ":ACQ:STATE OFF"], stdout=subprocess.PIPE)  # Replace with actual pyvisa command
    subprocess.run(["echo", ":WAV:DATA?"], stdout=subprocess.PIPE)     # Placeholder for waveform read

def acquisition_thread():
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
    READ_ALL_AVAILABLE = -1

    deriv = RealTimeDerivative(threshold=-.5)
    acquisition = False

    while True:
        read_result = hat.a_in_scan_read(READ_ALL_AVAILABLE, timeout)

        if read_result.hardware_overrun or read_result.buffer_overrun:
            print("Buffer overrun")
            break

        samples_read_per_channel = int(len(read_result.data) / num_channels)
        if samples_read_per_channel > 0:
            index = samples_read_per_channel * num_channels - num_channels
            voltage = read_result.data[index]

            if not acquisition:
                if deriv.update(voltage):
                    trigger_scope_start()
                    deriv.threshold = -30
                    acquisition = True
            else:
                if deriv.update(voltage):
                    trigger_scope_stop()
                    deriv.threshold = -0.5
                    acquisition = False

        time.sleep(0.05)