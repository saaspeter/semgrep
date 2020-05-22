import json
from pathlib import Path
from ruamel.yaml import YAML

from semgrep.constants import RULES_KEY
from semgrep.dump_ast import parsed_ast
from semgrep.pattern_lints import lint, EquivalentPatterns
from semgrep.rule import Rule


def autofix(path: Path):
    print(f'Autofixing {path} ...', end='')
    yaml = YAML(typ='rt')
    yaml.preserve_quotes = True
    yaml.width = 120
    with open(path) as f:
        code = yaml.load(f)
    # repeat changes
    changed = False
    while _autofix_yaml(code):
        changed = True

    if changed:
        with open(path, 'w') as wp:
            yaml.dump(code, wp)
    print()


def try_remove_return(pattern, lang):
    if not 'return' in pattern:
        import pdb; pdb.set_trace()
        raise Exception('broken')
    current_json = json.loads(parsed_ast(to_json=True, language=lang, pattern=pattern, targets=()))
    expected_json = dict(current_json)
    expected_json['Ss'][-1] = {'ExprStmt': current_json['Ss'][-1]['Return'][1]['some']}
    fixed_pattern = pattern.replace('return ', '')
    new_json = json.loads(parsed_ast(to_json=True, language=lang, pattern=fixed_pattern, targets=()))
    if new_json == expected_json:
        return fixed_pattern
    else:
        import pdb; pdb.set_trace()
        return None


def _autofix_yaml(yaml_tree) -> bool:
    change_made = False
    for rule_raw in yaml_tree.get(RULES_KEY):
        rule = Rule(rule_raw)
        lint_result = lint(rule.expression, rule.languages[0], yaml_tree)
        for result in lint_result:
            (pattern_either, li, ri, equivalence) = result.internal
            if equivalence == EquivalentPatterns.ExactMatch:
                print('.', end='')
                popped_pattern = pattern_either.raw.pop(ri)
                change_made = True
                if popped_pattern != pattern_either.raw[li]:
                    raise Exception('Something is broken!!!')
                    pass
                break
            elif equivalence == EquivalentPatterns.ReturnPairedWithAssignment:
                with_return = [x for x in (li, ri) if 'return' in 'return ' in pattern_either.raw[x]['pattern']][0]
                new_pattern = try_remove_return(pattern_either.raw[with_return]['pattern'], rule.languages[0])
                if new_pattern is not None:
                    pattern_either.raw[with_return]['pattern'] = new_pattern
                without_return = li if with_return == ri else ri
                pattern_either.raw.pop(without_return)
                change_made = True
                break
    return change_made
