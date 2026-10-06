import glob
import html
import os
from pathlib import Path
import sys
import tempfile
import xml.etree.ElementTree as ET


def read_results(pattern):
    files = glob.glob(pattern, recursive=True)
    if not files:
        raise ValueError('JUnit ausente')
    cases = [case for name in files for case in ET.parse(name).iter('testcase')]
    if not cases:
        raise ValueError('JUnit vazio')
    return [(case.get('name', 'sem nome'),
             'falhou' if case.find('failure') is not None or case.find('error') is not None
             else 'ignorado' if case.find('skipped') is not None else 'passou') for case in cases]


def self_test():
    with tempfile.TemporaryDirectory() as directory:
        report = Path(directory) / 'junit.xml'
        for content in ('', '<testsuite/>'):
            report.write_text(content)
            try:
                read_results(str(report))
            except (ValueError, ET.ParseError):
                pass
            else:
                raise AssertionError('Invalid report was accepted')
        report.write_text('<testsuite><testcase name="ok"/><testcase name="bad"><failure/></testcase><testcase name="skip"><skipped/></testcase></testsuite>')
        assert [status for _, status in read_results(str(report))] == ['passou', 'falhou', 'ignorado']
        try:
            read_results(str(Path(directory) / 'missing.xml'))
        except ValueError:
            pass
        else:
            raise AssertionError('Missing report was accepted')
    print('Summary parser checks passed')


if __name__ == '__main__':
    if '--self-test' in sys.argv:
        self_test()
        raise SystemExit(0)
    cases, problem = [], ''
    try:
        cases = read_results(os.environ.get('JUNIT_PATTERN', 'results/junit.xml'))
    except (OSError, ValueError, ET.ParseError) as error:
        problem = str(error)
    expected = int(os.environ['EXPECTED_TESTS'])
    outcome = os.environ.get('TEST_OUTCOME', 'unknown')
    passed = not problem and len(cases) == expected and all(status == 'passou' for _, status in cases) and outcome == 'success'
    lines = ['## LangChain — orchestration contracts (offline)', '', f"Etapa: **{outcome}**. Gate: **{'aprovado' if passed else 'reprovado'}**.",
             f'Casos registrados: **{len(cases)}/{expected}**. {html.escape(problem)}', '',
             '| Cenário | Resultado |', '| --- | --- |']
    lines += [f"| {html.escape(name).replace('|', '&#124;')} | {status} |" for name, status in cases]
    lines += ['', html.escape(os.environ.get('TEST_SCOPE', 'Escopo não informado.')),
              '', 'Relatórios gerados ficam no artifact desta run. Retenção: 14 dias.']
    content = '\n'.join(lines) + '\n'
    Path('results').mkdir(exist_ok=True)
    Path('results/summary.md').write_text(content, encoding='utf-8')
    if os.environ.get('GITHUB_STEP_SUMMARY'):
        with open(os.environ['GITHUB_STEP_SUMMARY'], 'a', encoding='utf-8') as output:
            output.write(content)
    print(content)
    raise SystemExit(0 if passed else 1)

