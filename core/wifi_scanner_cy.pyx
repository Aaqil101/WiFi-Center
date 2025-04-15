# wifi_scanner_cy.pyx - Cythonized functions for wifi_scanner.py

# cython: language_level=3
# cython: boundscheck=False
# cython: wraparound=False
# cython: cdivision=True

import time
import datetime
from collections import defaultdict
from typing import Dict, List, Set

# PyWiFi types - using python objects since we need the library functionality
from pywifi import PyWiFi, const, iface

# For type definitions
from cpython cimport datetime
from libc.stdlib cimport malloc, free
from libc.string cimport strcmp

# Define C types for better performance
ctypedef int signal_t
ctypedef double timestamp_t

cdef inline int clamp(int value, int min_val, int max_val) nogil:
    """Clamp a value between min and max values."""
    if value < min_val:
        return min_val
    elif value > max_val:
        return max_val
    return value

cdef inline int signal_to_percentage(int dbm_value) nogil:
    """Convert signal strength (dBm) to percentage (0-100%) using C implementation."""
    cdef int signal_strength = clamp((dbm_value + 100) * 2, 0, 100)
    return signal_strength

def get_wifi_interface():
    """Get the first available WiFi interface."""
    try:
        wifi = PyWiFi()
        if wifi.interfaces():
            return wifi.interfaces()[0]
        else:
            return None
    except Exception:
        return None

def cy_scan_wifi_networks():
    """
    Optimized Cython version of scan_wifi_networks.
    
    Returns:
        A list of dictionaries containing network information
    """
    cdef:
        list scan_results
        str ssid
        int signal_percent
        bint requires_login
        dict network_entry
        object interface = get_wifi_interface()
        
    if interface is None:
        return []
        
    # Get saved profiles (connections)
    cdef set saved_profiles = {profile.ssid for profile in interface.network_profiles()}
    
    # Trigger scan
    interface.scan()
    
    # Wait for scan to complete - this is I/O bound so we can't optimize much
    time.sleep(1.0)
    
    # Get scan results
    scan_results = interface.scan_results()
    
    # Process scan results - optimize this portion with Cython
    cdef:
        dict networks_dict = {}
        str current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
        int i, n = len(scan_results)
        
    for i in range(n):
        result = scan_results[i]
        ssid = result.ssid
        
        if not ssid:  # Skip networks with empty SSIDs
            continue
            
        # Convert signal strength (dBm) to percentage (0-100%) using optimized function
        signal_percent = signal_to_percentage(result.signal)
        
        # Check if authentication is required
        requires_login = (result.akm[0] != const.AKM_TYPE_NONE and ssid not in saved_profiles)
        
        # Keep only the strongest signal for each SSID
        if ssid not in networks_dict or signal_percent > networks_dict[ssid]["strength"]:
            networks_dict[ssid] = {
                "ssid": ssid,
                "strength": signal_percent,
                "requires_login": requires_login,
                "last_seen": current_time,
            }
    
    # Convert to list and sort
    result_list = sorted(networks_dict.values(), key=lambda x: x["strength"], reverse=True)
    
    # Return top 6 networks by signal strength
    return result_list[:6]
