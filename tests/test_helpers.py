import pytest

from xnclient.helpers import hextoint
from xnclient.helpers import fromhex

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
# 
#

def test_fromhex_invalid_length():
    assert fromhex('A\n') is None

def test_fromhex_no_data():
    assert fromhex('\n') is None
    
def test_fromhex_single():
    result = fromhex('27\n')
    assert len(result) == 1
    assert result[0] == 39

def test_fromhex_estop():
    result = fromhex('60810081\n')
    assert len(result) == 4
    assert result[0] == 96
    assert result[1] == 129
    assert result[2] == 0
    assert result[3] == 129
