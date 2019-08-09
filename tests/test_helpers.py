import pytest

from xnclient.helpers import hextoint, hextobytes, Exchange

#
# Test low level conversions
#

def test_hextoint_0():
    assert hextoint('0') == 0

def test_hextoint_9():
    assert hextoint('9') == 9

def test_hextoint_A():
    assert hextoint('A') == 10
   
def test_hextoint_F():
    assert hextoint('F') == 15

#
# Test basic hex string conversions
#

def test_hextobytes_invalid_length():
    assert hextobytes('A\n') is None

def test_hextobytes_no_data():
    assert hextobytes('\n') is None
    
def test_hextobytes_single():
    result = hextobytes('27\n')
    assert len(result) == 1
    assert result[0] == 39

def test_hextobytes_estop():
    result = hextobytes('60810081\n')
    assert len(result) == 4
    assert result[0] == 96
    assert result[1] == 129
    assert result[2] == 0
    assert result[3] == 129

#
#
#

def test_Exchange_1():
    e = Exchange(hextobytes('41\n'))
    print(e)
