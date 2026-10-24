import pytest
from fnaf_desktop.core import normalize, load, save

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

def test_escape_requires_continuous_five_seconds():
    from fnaf_desktop.core import HoldToQuit
    hold = HoldToQuit()
    assert not hold.update(True, 10)
    assert not hold.update(True, 14.999)
    assert not hold.update(False, 14.999)
    assert not hold.update(True, 20)
    assert not hold.update(True, 24.999)
    assert hold.update(True, 25)


def test_image_setting_defaults_and_validation():
    assert normalize({})['image_popups'] is True
    assert normalize({'image_popups': False})['image_popups'] is False


def test_config_v2_migrates_legacy_and_clamps(tmp_path):
    import json
    path = tmp_path/'config.json'
    (tmp_path/'settings.json').write_text(json.dumps({'silent':True, 'activity':{'Foxy':99,'Bonnie':-1}, 'fps':1000, 'max_images':999}))
    result = load(path)
    assert result['silent']
    assert result['activity']['Foxy'] == 20 and result['activity']['Bonnie'] == 0
    assert result['fps'] == 60 and result['max_images'] == 12
    save(path, result)
    assert path.is_file() and load(path) == result
    assert normalize({'activity':{'Freddy':'bad'}})['activity']['Freddy'] == 10
    assert normalize({'activity':None, 'fps':float('inf')})['fps'] == 60
