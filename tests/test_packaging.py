import os

import qmt_sdk


def test_strategy_templates_are_discoverable():
    template_dir = qmt_sdk.get_template_dir()
    assert os.path.isfile(os.path.join(template_dir, "XTQUANT_COMPAT_BRIDGE.py"))
    assert os.path.isfile(os.path.join(template_dir, "XTQUANT_COMPAT_BRIDGE_LAUNCHER.py"))
