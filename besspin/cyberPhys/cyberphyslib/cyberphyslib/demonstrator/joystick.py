"""
Project: SSITH CyberPhysical Demonstrator
joystick.py
Author: Ethan Lew <elew@galois.com>
Date: 05/28/2021
Python 3.8.3
O/S: Windows 10

User Inputs Activity Monitoring Component
"""
import enum
import pygame
from collections import deque
import numpy as np
from .component import ComponentPoller, ComponentStatus
import cyberphyslib.demonstrator.config as cconf


class T150Axes(enum.IntEnum):
    """axis indicies for T150 Thrustmaster"""
    STEERING_WHEEL = 0
    BRAKE = 1
    THROTTLE = 2


def init_joystick(joy_name: str) -> pygame.joystick.Joystick:
    """get pygame joystick object from device name string"""
    pygame.init()

    joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
    tm_joy = None

    for joy in joysticks:
        joy.init()
        if joy.get_name() == joy_name:
            if tm_joy is None:
                tm_joy = joy
            else:
                raise RuntimeError(f"More than one racing wheel '{joy_name}' is connected!")

    if tm_joy is None:
        raise RuntimeError(f"No racing wheel '{joy_name}' is connected!")
    return tm_joy


class JoystickMonitorComponent(ComponentPoller):
    """Activity Monitor for the Steering Wheel

    Sample at an update rate, filling up a window of n length. If range is less
    than a threshold, output an inactive status. Otherwise, output an active status.
    """
    update_rate = 2

    def __init__(self, joy_name: str, window_length = 50, threshold=1E-2):
        super().__init__("jmonitor", [(cconf.DIRECTOR_PORT, "jmonitor-commands")],
                                       [(cconf.JMONITOR_PORT, "jmonitor-events"),
                                        (cconf.JMONITOR_PORT, "jmonitor-beamng")],
                         sample_frequency= self.update_rate)
        # TODO: log joy info
        self.maxlen = window_length
        self.window =  deque([], maxlen=window_length)
        self.threshold = threshold
        self._no_joystick = True
        self.joy_name = joy_name
        self.joystick = None

    def on_start(self):
        """initialize pygame"""
        pygame.init()
        self.start_poller()
        try:
            self.joystick = init_joystick(self.joy_name)
            self._no_joystick = False
        except Exception as exc:
            self.joystick =  None
            self._no_joystick = True

    def wait_ready_command(self):
        import time
        while not self._start_finished:
            time.sleep(0.5)
        return ComponentStatus.READY if not self._no_joystick else ComponentStatus.ERROR

    def on_poll_poll(self, t):
        """fill up window of steering wheel observations"""
        edge = self.is_active
        if self.joystick:
            _ = pygame.event.get() # TODO: is this necessary?
            ret = self.joystick.get_axis(T150Axes.STEERING_WHEEL)
            self.window.append(ret)
        if edge is not self.is_active:
            if edge:
                print("FALLING EDGE (inactive)")
            else:
                print("RISING EDGE (active)")

    @property
    def is_active(self):
        """evaluate activity condition"""
        if len(self.window) < self.maxlen:
            return True
        else:
            warr = np.array(self.window)
            rge = max(warr) - min(warr)
            return rge > self.threshold

    @property
    def is_inactive(self):
        """evaluate inactivity condition"""
        return not self.is_active
