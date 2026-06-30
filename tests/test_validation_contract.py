from system.validation_report import validation_report 

def test_validation_contract():
    data = validation_report.run()
    assert 'build' in data
    assert 'imports' in data
    assert 'apis' in data
