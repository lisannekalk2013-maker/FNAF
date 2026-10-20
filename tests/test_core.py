import pytest
from fnaf_desktop.core import normalize, load, save, VolumeGuard

@pytest.mark.parametrize('value,expected', [(1, .5), (-1, 0), ('bad', .15), (float('nan'), .15)])
def test_volume_clamped(value, expected):
    assert normalize({'volume': value})['volume'] == expected

def test_settings_roundtrip_and_corruption(tmp_path):
    path = tmp_path/'settings.json'
    save(path, {'silent': True, 'characters': ['Freddy', 'invalid']})
    assert load(path)['silent']
    assert load(path)['characters'] == ['Freddy']
    path.write_text('{broken')
    assert load(path)['volume'] == .15

class Endpoint:
    def __init__(self, value): self.value = value
    def GetMasterVolumeLevelScalar(self): return self.value
    def SetMasterVolumeLevelScalar(self, value, _): self.value = value

@pytest.mark.parametrize('initial', [.05, .8])
def test_volume_never_raised_and_restored(initial):
    endpoint = Endpoint(initial)
    guard = VolumeGuard(endpoint)
    guard.begin(.15)
    assert endpoint.value == min(initial, .15)
    guard.begin(.1)
    guard.restore()
    assert endpoint.value == initial
    guard.restore()
    assert endpoint.value == initial

def test_failed_restore_can_be_retried():
    endpoint = Endpoint(.8)
    guard = VolumeGuard(endpoint)
    guard.begin(.15)
    setter = endpoint.SetMasterVolumeLevelScalar
    def fail(*args): raise RuntimeError('device temporarily unavailable')
    endpoint.SetMasterVolumeLevelScalar = fail
    with pytest.raises(RuntimeError): guard.restore()
    assert guard.original == .8
    endpoint.SetMasterVolumeLevelScalar = setter
    guard.restore()
    assert endpoint.value == .8
