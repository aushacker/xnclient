import pytest

from xnclient.helpers import hex_to_int, hex_to_bytes, Exchange

#
# Test low level conversions
#

def test_hex_to_int_0():
    assert hex_to_int('0') == 0

def test_hex_to_int_9():
    assert hex_to_int('9') == 9

def test_hex_to_int_A():
    assert hex_to_int('A') == 10
       
def test_hex_to_int_a():
    assert hex_to_int('a') == 10
           
def test_hex_to_int_F():
    assert hex_to_int('F') == 15
    
def test_hex_to_int_f():
    assert hex_to_int('f') == 15
        
def test_hex_to_int_s():
    assert hex_to_int('s') is None

#
# Test basic hex string conversions
#

def test_hex_to_bytes_invalid_length():
    assert hex_to_bytes('A\n') is None

def test_hex_to_bytes_no_data():
    assert hex_to_bytes('\n') is None
    
def test_hex_to_bytes_single():
    result = hex_to_bytes('27\n')
    assert len(result) == 1
    assert result[0] == 39

def test_hex_to_bytes_estop():
    result = hex_to_bytes('60810081\n')
    assert len(result) == 4
    assert result[0] == 96
    assert result[1] == 129
    assert result[2] == 0
    assert result[3] == 129

# 5D is only valid byte pairing in message
def test_hex_to_bytes_invalid_data():
    result = hex_to_bytes('e\\5Ds0\n')
    assert len(result) == 1
    assert result[0] == 93
 
#
#
#

def test_Exchange_normal_enquiry():
    e = Exchange.parse('41\n')
    assert e.isvalid
    assert e.address == 1
    assert e.short_desc() == 'CS Normal Enquiry'

# A call byte can never be followed by a single response byte (i.e. missing CRC)
def test_Exchange_missing_crc():
    e = Exchange.parse('4100\n')
    assert not e.isvalid
    
def test_Exchange_ack_response():
    e = Exchange.parse('422020\n')
    assert e.isvalid
    assert e.address == 2
    assert e.short_desc() == 'D  Acknowledgement response'
        
def test_Exchange_resume_operations_request():
    e = Exchange.parse('C32181A0\n')
    assert e.isvalid
    assert e.address == 3
    assert e.short_desc() == 'D  Resume operations request'
            
def test_Exchange_stop_operations_request():
    e = Exchange.parse('442180A1\n')
    assert e.isvalid
    assert e.address == 4
    assert e.short_desc() == 'D  Stop operations request (emergency off)'
                
                                    