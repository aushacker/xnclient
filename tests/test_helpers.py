import pytest

from xnclient.helpers import Exchange

#
# Test basic hex string conversions
#

def test_Exchange_parse_empty():
    with pytest.raises(ValueError):
        Exchange.parse('')

def test_Exchange_parse_lf_only():
    with pytest.raises(ValueError):
        Exchange.parse('\n')

def test_Exchange_parse_odd_nybble():
    with pytest.raises(ValueError):
        Exchange.parse('A')

def test_Exchange_parse_non_hex():
    with pytest.raises(ValueError):
        Exchange.parse('Ds')

#
# Basic command station operations and general weirdness
#

def test_Exchange_normal_enquiry():
    e = Exchange.parse('41')
    assert e.isvalid
    assert e.isenquiry
    assert e.address == 1
    assert e.short_desc() == 'CS Normal Enquiry'

# A call byte can never be followed by a single response byte (i.e. missing CRC)
def test_Exchange_missing_crc():
    e = Exchange.parse('41 00')
    assert not e.isvalid

def test_Exchange_TBD():
    e = Exchange.parse('21')
    assert e.isvalid
    assert not e.isenquiry
    assert e.address == 1
    assert e.short_desc() == 'TBD (Future Command)'

#
# Broadcasts from command station to all devices
#

# 2.1.4.1
def test_Exchange_normal_operation_resumed():
    e = Exchange.parse('60 61 01 60')
    assert e.isvalid
    assert not e.isenquiry
    assert e.address == 0
    assert e.short_desc() == 'CS Normal operation resumed'

# 2.1.4.2
def test_Exchange_track_power_off():
    e = Exchange.parse('60 61 00 61')
    assert e.isvalid
    assert not e.isenquiry
    assert e.address == 0
    assert e.short_desc() == 'CS Track power off'

# 2.1.4.3
def test_Exchange_emergency_stop():
    e = Exchange.parse('60 81 00 81')
    assert e.isvalid
    assert not e.isenquiry
    assert e.address == 0
    assert e.short_desc() == 'CS Emergency stop'

# 2.1.4.4
def test_Exchange_service_mode_entry():
    e = Exchange.parse('60 61 02 63')
    assert e.isvalid
    assert not e.isenquiry
    assert e.address == 0
    assert e.short_desc() == 'CS Service mode entry'

# 2.1.4.5
def test_Exchange_feedback_broadcast():
    e = Exchange.parse('A0 41 00 00 41')
    assert e.isvalid
    assert not e.isenquiry
    assert e.address == 0
    assert e.short_desc() == 'CS Feedback broadcast'

#
# Test messages from the command station to the device
#

# 2.1.5.1
def test_Exchange_prog_info_short_circuit():
    e = Exchange.parse('E1 61 12 73')
    assert e.isvalid
    assert not e.isenquiry
    assert e.address == 1
    assert e.short_desc() == 'CS Programming info (short circuit)'

# 2.1.5.2
def test_Exchange_prog_info_not_found():
    e = Exchange.parse('E2 61 13 72')
    assert e.isvalid
    assert not e.isenquiry
    assert e.address == 2
    assert e.short_desc() == 'CS Programming info (data byte not found)'

# 2.1.5.3
def test_Exchange_prog_info_cs_busy():
    e = Exchange.parse('63 61 1F 7E')
    assert e.isvalid
    assert not e.isenquiry
    assert e.address == 3
    assert e.short_desc() == 'CS Programming info (command station busy)'

# 2.1.5.4
def test_Exchange_prog_info_cs_ready():
    e = Exchange.parse('E4 61 11 70')
    assert e.isvalid
    assert not e.isenquiry
    assert e.address == 4
    assert e.short_desc() == 'CS Programming info (command station ready)'

# 2.1.5.5
def test_Exchange_service_mode_paged():
    e = Exchange.parse('65 63 10 00 00 73')
    assert e.isvalid
    assert not e.isenquiry
    assert e.address == 5
    assert e.short_desc() == 'CS Service mode response (register and paged)'

# 2.1.5.6
def test_Exchange_service_mode_cv():
    e = Exchange.parse('66 63 14 00 00 77')
    assert e.isvalid
    assert not e.isenquiry
    assert e.address == 6
    assert e.short_desc() == 'CS Service mode response (direct cv)'

# 2.1.6.1
def test_Exchange_sw_version_v1v2():
    e = Exchange.parse('E7 62 21 23 60')
    assert e.isvalid
    assert not e.isenquiry
    assert e.address == 7
    assert e.short_desc() == 'CS Software version (XBus V1 and V2)'

# 2.1.6.2
def test_Exchange_sw_version_xpressnet():
    e = Exchange.parse('E8 63 21 30 00 72')
    assert e.isvalid
    assert not e.isenquiry
    assert e.address == 8
    assert e.short_desc() == 'CS Software version (XpressNet)'

# 2.1.7
def test_Exchange_cs_status():
    e = Exchange.parse('69 62 22 00 40')
    assert e.isvalid
    assert not e.isenquiry
    assert e.address == 9
    assert e.short_desc() == 'CS Command station status'

# 2.1.8
def test_Exchange_transfer_errors():
    e = Exchange.parse('6A 61 80 E1')
    assert e.isvalid
    assert not e.isenquiry
    assert e.address == 10
    assert e.short_desc() == 'CS Transfer errors'

# 2.1.9
def test_Exchange_cs_busy():
    e = Exchange.parse('EB 61 81 E0')
    assert e.isvalid
    assert not e.isenquiry
    assert e.address == 11
    assert e.short_desc() == 'CS Command station busy'

# 2.1.10
def test_Exchange_unsupported_instruction():
    e = Exchange.parse('6C 61 82 E3')
    assert e.isvalid
    assert not e.isenquiry
    assert e.address == 12
    assert e.short_desc() == 'CS Unsupported instruction'

#
# Test messages from the device to the command station
#

# 2.2.1
def test_Exchange_ack_response():
    e = Exchange.parse('41 20 20')
    assert e.isvalid
    assert e.address == 1
    assert e.short_desc() == 'D  Acknowledgement response'

# 2.2.2
def test_Exchange_resume_operations_request():
    e = Exchange.parse('42 21 81 A0\n')
    assert e.isvalid
    assert e.address == 2
    assert e.short_desc() == 'D  Resume operations request'
            
# 2.2.3
def test_Exchange_stop_operations_request():
    e = Exchange.parse('C3 21 80 A1')
    assert e.isvalid
    assert e.address == 3
    assert e.short_desc() == 'D  Stop operations request (emergency off)'

# 2.2.14
def test_Exchange_command_station_sw_version_request():
    e = Exchange.parse('41 21 21 00')
    assert e.isvalid
    assert not e.isenquiry
    assert e.address == 1
    assert e.short_desc() == 'D  Command station software version request'
            
# 2.2.15
def test_Exchange_command_station_status_request():
    e = Exchange.parse('42 21 24 05')
    assert e.isvalid
    assert not e.isenquiry
    assert e.address == 2
    assert e.short_desc() == 'D  Command station status request'            
