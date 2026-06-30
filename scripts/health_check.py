from system.validation_report import validation_report

if __name__ == '__main__':
    result = validation_report.run() 
    print(result)
    failed = [k for k,v in result.items() if v not in ('PASS','CONFIGURED')]
    raise SystemExit(1 if failed else 0)
