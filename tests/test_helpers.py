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
    assert e.short_desc() == 'CS Command station status response'

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

# 2.1.11
def test_Exchange_accessory_decoder_information_response():
    e = Exchange.parse('ED 42 00 00 42')
    assert e.isvalid
    assert not e.isenquiry
    assert e.address == 13
    assert e.short_desc() == 'CS Accessory decoder information response'

# 2.1.12.1
def test_Exchange_loco_available_response_v1():
    e = Exchange.parse('EE 83 03 00 00 80')
    assert e.isvalid
    assert not e.isenquiry
    assert e.address == 14
    assert e.short_desc() == 'CS Locomotive is available for operation (V1)'

# 2.1.12.2
def test_Exchange_loco_poached_response_v1():
    e = Exchange.parse('6F A3 03 00 00 A0')
    assert e.isvalid
    assert not e.isenquiry
    assert e.address == 15
    assert e.short_desc() == 'CS Locomotive is being operated by another device (V1)'

# 2.1.13.1
def test_Exchange_loco_available_response_v2():
    e = Exchange.parse('F0 84 03 00 00 00 87')
    assert e.isvalid
    assert not e.isenquiry
    assert e.address == 16
    assert e.short_desc() == 'CS Locomotive is available for operation (V2)'

# 2.1.13.2
def test_Exchange_loco_poached_response_v2():
    e = Exchange.parse('71 A4 03 00 00 00 A7')
    assert e.isvalid
    assert not e.isenquiry
    assert e.address == 17
    assert e.short_desc() == 'CS Locomotive is being operated by another device (V2)'

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

# 2.2.4
def test_Exchange_stop_all_locos_request():
    e = Exchange.parse('44 80 80')
    assert e.isvalid
    assert e.address == 4
    assert e.short_desc() == 'D  Stop all locomotives request (emergency stop)'

# 2.2.5.1
def test_Exchange_estop_loco_request_v1v2():
    e = Exchange.parse('C5 91 03 92')
    assert e.isvalid
    assert e.address == 5
    assert e.short_desc() == 'D  Emergency stop a locomotive (V1 and V2)'

# 2.2.5.2
def test_Exchange_estop_loco_request_xpressnet():
    e = Exchange.parse('C6 92 00 03 91')
    assert e.isvalid
    assert e.address == 6
    assert e.short_desc() == 'D  Emergency stop a locomotive (XpressNet)'

# 2.2.6
# 2.2.7
# 2.2.8

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

# 2.2.17
def test_Exchange_accessory_decoder_information_request():
    e = Exchange.parse('D1 42 00 80 C2')
    assert e.isvalid
    assert not e.isenquiry
    assert e.address == 17
    assert e.short_desc() == 'D  Accessory decoder information request'            

# 2.2.18
def test_Exchange_accessory_decoder_operation_request():
    e = Exchange.parse('D2 52 00 88 DA')
    assert e.isvalid
    assert not e.isenquiry
    assert e.address == 18
    assert e.short_desc() == 'D  Accessory decoder operation request'            

# 2.2.19.1
def test_Exchange_loco_information_request_v1():
    e = Exchange.parse('53 A1 03 A2')
    assert e.isvalid
    assert not e.isenquiry
    assert e.address == 19
    assert e.short_desc() == 'D  Locomotive information request (V1)'            

# 2.2.19.2
def test_Exchange_loco_information_request_v1v2():
    e = Exchange.parse('D4 A2 03 00 A1')
    assert e.isvalid
    assert not e.isenquiry
    assert e.address == 20
    assert e.short_desc() == 'D  Locomotive information request (V1 and V2)'            

# 2.2.19.3
def test_Exchange_loco_information_request_xn():
    e = Exchange.parse('55 E3 00 00 03 E0')
    assert e.isvalid
    assert not e.isenquiry
    assert e.address == 21
    assert e.short_desc() == 'D  Locomotive information request (XpressNet)'            

# 2.2.19.4
def test_Exchange_function_status_request_xn():
    e = Exchange.parse('56 E3 07 00 03 E7')
    assert e.isvalid
    assert not e.isenquiry
    assert e.address == 22
    assert e.short_desc() == 'D  Function status request (XpressNet)'            

# 2.2.20.1
def test_Exchange_loco_operations_v1():
    e = Exchange.parse('D7 B3 03 4F 00 FF')
    assert e.isvalid
    assert not e.isenquiry
    assert e.address == 23
    assert e.short_desc() == 'D  Locomotive operations (V1)'            

# 2.2.20.2
def test_Exchange_loco_operations_v2():
    e = Exchange.parse('D8 B4 03 4F 00 00 F8')
    assert e.isvalid
    assert not e.isenquiry
    assert e.address == 24
    assert e.short_desc() == 'D  Locomotive operations (V2)'            

# 2.2.20.3
def test_Exchange_loco_speed_and_direction_14_xn():
    e = Exchange.parse('59 E4 10 00 03 0F F8')
    assert e.isvalid
    assert not e.isenquiry
    assert e.address == 25
    assert e.short_desc() == 'D  Locomotive speed and direction 14 (XpressNet)'            
#
def test_Exchange_loco_speed_and_direction_27_xn():
    e = Exchange.parse('59 E4 11 00 03 1F E9')
    assert e.isvalid
    assert not e.isenquiry
    assert e.address == 25
    assert e.short_desc() == 'D  Locomotive speed and direction 27 (XpressNet)'            
#
def test_Exchange_loco_speed_and_direction_28_xn():
    e = Exchange.parse('59 E4 12 00 03 1F EA')
    assert e.isvalid
    assert not e.isenquiry
    assert e.address == 25
    assert e.short_desc() == 'D  Locomotive speed and direction 28 (XpressNet)'            
#
def test_Exchange_loco_speed_and_direction_128_xn():
    e = Exchange.parse('59 E4 13 00 03 7F 8B')
    assert e.isvalid
    assert not e.isenquiry
    assert e.address == 25
    assert e.short_desc() == 'D  Locomotive speed and direction 128 (XpressNet)'            
# 2.2.20.4
# 2.2.20.5
